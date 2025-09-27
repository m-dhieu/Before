#--------------------------------------------------------------------------------
# Script Name: parse_xml.py
# Description: Parses the modified_sms_v2.xml file in Python 
#              Converts SMS records into JSON objects (list of dictionaries)
# Author: Monica Dhieu
# Date:   2025-09-27
# Usage:  python3 parse_xml.py
#--------------------------------------------------------------------------------

import xml.etree.ElementTree as ET
from datetime import datetime
import re
import json

def parse_sms_date(ms_timestamp):
    """
    Converts milliseconds to a formatted datetime string: '%Y-%m-%d %H:%M:%S'.
    """
    ts = int(ms_timestamp) / 1000
    return datetime.utcfromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')

def extract_transaction_info(body):
    """
    Parses SMS text and extract transaction details:
    amount, currency, transaction type, datetime, reference ID,
    balance after transaction, status, and full message text.
    """
    transaction = {}
    amount_match = re.search(r'([\d,]+) (\w{3})', body)
    if amount_match:
        transaction['Amount'] = float(amount_match.group(1).replace(',', ''))
        transaction['Currency'] = amount_match.group(2)
    if 'received' in body.lower():
        transaction['TransactionType'] = 'deposit'
    elif 'payment' in body.lower():
        transaction['TransactionType'] = 'payment'
    elif 'transferred' in body.lower():
        transaction['TransactionType'] = 'transfer'
    elif 'withdrawal' in body.lower():
        transaction['TransactionType'] = 'withdrawal'
    else:
        transaction['TransactionType'] = 'other'
    dt_match = re.search(r'at (\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})', body)
    transaction['DateTime'] = dt_match.group(1) if dt_match else None
    ref_match = re.search(r'(Financial Transaction Id:|TxId:)\s*([\d]+)', body)
    transaction['ReferenceNumber'] = ref_match.group(2) if ref_match else None
    bal_match = re.search(r'new balance:?([\d,]+) (\w{3})', body.lower())
    transaction['BalanceAfterTransaction'] = float(bal_match.group(1).replace(',', '')) if bal_match else None
    transaction['Status'] = 'confirmed'  # Default
    transaction['MessageText'] = body.replace("'", "''") if body else ''
    return transaction

def extract_users(body):
    """
    Extracts user details from SMS text (sender and receiver info).
    """
    users = []
    sender_match = re.search(r'from ([\w\s]+) \(([*\d]+)\)', body)
    if sender_match:
        users.append({
            'Name': sender_match.group(1).strip(),
            'PhoneNumber': sender_match.group(2).strip(),
            'UserType': 'sender'
        })
    receiver_match = re.search(r'to ([\w\s]+) (\d+)', body)
    if receiver_match:
        users.append({
            'Name': receiver_match.group(1).strip(),
            'PhoneNumber': receiver_match.group(2).strip(),
            'UserType': 'receiver'
        })
    else:
        receiver_match2 = re.search(r'to ([\w\s]+) \(([\d]+)\)', body)
        if receiver_match2:
            users.append({
                'Name': receiver_match2.group(1).strip(),
                'PhoneNumber': receiver_match2.group(2).strip(),
                'UserType': 'receiver'
            })
    return users

def load_transactions(file_path):
    """
    Parses the XML file and returns a list of transaction dicts for JSON serialization.
    """
    tree = ET.parse(file_path)
    root = tree.getroot()
    user_id_map = {}
    user_counter = 1
    transaction_counter = 1

    transactions = []

    for sms in root.findall('sms'):
        body = sms.attrib.get('body')
        date_ms = sms.attrib.get('date')
        sms_datetime = parse_sms_date(date_ms) if date_ms else None

        transaction_info = extract_transaction_info(body)
        if not transaction_info.get('DateTime'):
            transaction_info['DateTime'] = sms_datetime

        users = extract_users(body)
        for u in users:
            key = (u['Name'], u['PhoneNumber'], u['UserType'])
            if key not in user_id_map:
                user_id_map[key] = user_counter
                user_counter += 1
                u['UserID'] = user_id_map[key]
            else:
                u['UserID'] = user_id_map[key]

        transaction = {
            'TransactionID': transaction_counter,
            'TransactionType': transaction_info.get('TransactionType'),
            'Amount': transaction_info.get('Amount'),
            'Currency': transaction_info.get('Currency'),
            'DateTime': transaction_info.get('DateTime'),
            'ReferenceNumber': transaction_info.get('ReferenceNumber'),
            'BalanceAfterTransaction': transaction_info.get('BalanceAfterTransaction'),
            'Status': transaction_info.get('Status'),
            'MessageText': transaction_info.get('MessageText'),
            'Participants': users
        }
        transactions.append(transaction)
        transaction_counter += 1

    return transactions

def generate_sql_inserts(transactions):
    """
    From a list of transaction dicts, generate SQL insert statements for Users, Transactions, and TransactionParticipants.
    """
    user_id_set = set()
    sql_statements = []

    # Collect unique users from all transactions
    for tx in transactions:
        for p in tx['Participants']:
            user_id_set.add((p['UserID'], p['Name'], p['PhoneNumber'], p['UserType']))

    # Insert Users
    sql_statements.append('-- Insert Users')
    for uid, name, phone, utype in sorted(user_id_set, key=lambda x: x[0]):
        sql_statements.append(
            f"INSERT INTO User (UserID, Name, PhoneNumber, UserType) VALUES ({uid}, '{name.replace('\'','\'\'')}', '{phone}', '{utype}');"
        )
    sql_statements.append('')

    # Insert Transactions
    sql_statements.append('-- Insert Transactions')
    for tx in transactions:
        ref = tx['ReferenceNumber'] if tx['ReferenceNumber'] else 'NULL'
        if ref != 'NULL':
            ref = f"'{ref}'"
        amt = tx['Amount'] if tx['Amount'] is not None else 0
        curr = tx['Currency'] if tx['Currency'] else 'RWF'
        dt = tx['DateTime'] if tx['DateTime'] else 'NULL'
        if dt != 'NULL':
            dt = f"'{dt}'"
        balance = tx['BalanceAfterTransaction']
        balance_str = str(balance) if balance is not None else 'NULL'
        st = tx['Status'] if tx['Status'] else 'confirmed'
        msg = tx['MessageText'].replace("'", "''") if tx['MessageText'] else ''
        type_ = tx['TransactionType'] if tx['TransactionType'] else 'other'
        sql_statements.append(
            f"INSERT INTO Transaction (TransactionID, TransactionType, Amount, Currency, DateTime, ReferenceNumber, "
            f"BalanceAfterTransaction, Status, MessageText, CategoryID) "
            f"VALUES ({tx['TransactionID']}, '{type_}', {amt}, '{curr}', {dt}, {ref}, {balance_str}, '{st}', '{msg}', 1);"
        )
    sql_statements.append('')

    # Insert Participants
    sql_statements.append('-- Insert Transaction Participants')
    participant_counter = 1
    for tx in transactions:
        for p in tx['Participants']:
            sql_statements.append(
                f"INSERT INTO TransactionParticipant (ParticipantID, TransactionID, UserID, Role) "
                f"VALUES ({participant_counter}, {tx['TransactionID']}, {p['UserID']}, '{p['UserType']}');"
            )
            participant_counter += 1

    return '\n'.join(sql_statements)

if __name__ == '__main__':
    # Load transactions from XML file
    file_path = 'data/raw/modified_sms_v2.xml'
    all_transactions = load_transactions(file_path)

    # Print JSON for API use or verification
    json_output = json.dumps(all_transactions, indent=4)
    print("Parsed JSON transactions:")
    print(json_output)

    # Generate SQL for stored data
    sql_script = generate_sql_inserts(all_transactions)
    print("\nGenerated SQL Insert Statements:")
    print(sql_script)
