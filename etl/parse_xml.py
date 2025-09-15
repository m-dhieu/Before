import xml.etree.ElementTree as ET
from datetime import datetime
import re

def parse_sms_date(ms_timestamp):
    """
    Convert milliseconds timestamp string to a formatted datetime string.
    """
    ts = int(ms_timestamp) / 1000
    return datetime.utcfromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')

def extract_transaction_info(body):
    """
    Parse SMS body text and extract transaction details:
    amount, currency, type (deposit/payment/etc), datetime, reference ID,
    balance after transaction, status, and full message text.
    """
    transaction = {}
    amount_match = re.search(r'([\d,]+) (\w{3})', body)
    if amount_match:
        transaction['Amount'] = float(amount_match.group(1).replace(',', ''))
        transaction['Currency'] = amount_match.group(2)
    # Define transaction type
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
    # Extract timestamp from text
    dt_match = re.search(r'at (\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})', body)
    transaction['DateTime'] = dt_match.group(1) if dt_match else None
    # Extract Transaction ID
    ref_match = re.search(r'(Financial Transaction Id:|TxId:)\s*([\d]+)', body)
    transaction['ReferenceNumber'] = ref_match.group(2) if ref_match else None
    # Extract new balance after transaction
    bal_match = re.search(r'new balance:?([\d,]+) (\w{3})', body.lower())
    transaction['BalanceAfterTransaction'] = float(bal_match.group(1).replace(',', '')) if bal_match else None
    # Assume status confirmed if SMS received
    transaction['Status'] = 'confirmed'
    # Escape single quotes for insertion
    transaction['MessageText'] = body.replace("'", "''")
    return transaction

def extract_users(body):
    """
    Parse SMS body text to extract user data (senders and receivers),
    including name, phone number, and role in transaction.
    """
    users = []
    # Sender: 'from <Name> (<Phone>)'
    sender_match = re.search(r'from ([\w\s]+) \(([*\d]+)\)', body)
    if sender_match:
        users.append({
            'Name': sender_match.group(1).strip(),
            'PhoneNumber': sender_match.group(2).strip(),
            'UserType': 'sender'
        })
    # Receiver: 'to <Name> <Phone>' or 'to <Name> (<Phone>)'
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

def xml_to_sql(file_path):
    """
    Main function to parse XML file, extract data, and generate SQL insert statements, i.e:
    - Reads XML from file path
    - Iterates SMS entries, extracting transaction and user info.
    - Maps users and transactions to unique IDs
    - Outputs SQL inserts for Users, Transactions, and TransactionParticipants
    """
    # Parse XML file
    tree = ET.parse(file_path)
    root = tree.getroot()

    users = {}
    transactions = []
    transaction_participants = []

    user_id_map = {}      # Map user to unique id
    user_counter = 1
    transaction_counter = 1
    participant_counter = 1

    # Go through each sms element
    for sms in root.findall('sms'):
        body = sms.attrib.get('body')
        date_ms = sms.attrib.get('date')
        sms_datetime = parse_sms_date(date_ms) if date_ms else None

        # Extract transaction details
        transaction_info = extract_transaction_info(body)
        if not transaction_info.get('DateTime'):
            transaction_info['DateTime'] = sms_datetime

        # Extract users involved in the transaction
        sms_users = extract_users(body)

        # Register users
        for u in sms_users:
            key = (u['Name'], u['PhoneNumber'], u['UserType'])
            if key not in user_id_map:
                user_id_map[key] = user_counter
                user_counter += 1
                users[key] = u

        # Create transactions
        transactions.append({
            'TransactionID': transaction_counter,
            **transaction_info
        })

        # Create participants linking users to transactions
        for u in sms_users:
            participant = {
                'ParticipantID': participant_counter,
                'TransactionID': transaction_counter,
                'UserID': user_id_map[(u['Name'], u['PhoneNumber'], u['UserType'])],
                'Role': u['UserType']
            }
            participant_counter += 1
            transaction_participants.append(participant)

        transaction_counter += 1

    sql_inserts = []

    # Insert Users
    sql_inserts.append('-- Insert Users')
    for key, user in users.items():
        phone, name, utype = key[1], key[0].replace("'", "''"), key[2]
        sql_inserts.append(f"INSERT INTO User (UserID, PhoneNumber, Name, UserType) VALUES ({user_id_map[key]}, '{phone}', '{name}', '{utype}');")
    sql_inserts.append('')

    # Insert Transactions
    sql_inserts.append('-- Insert Transactions')
    for t in transactions:
        ref = t.get('ReferenceNumber') or 'NULL'
        if ref != 'NULL':
            ref = f"'{ref}'"
        amt = t.get('Amount') or 0
        curr = t.get('Currency') or 'RWF'
        dt = t.get('DateTime') or 'NULL'
        if dt != 'NULL':
            dt = f"'{dt}'"
        balance = t.get('BalanceAfterTransaction')
        balance_str = str(balance) if balance is not None else 'NULL'
        st = t.get('Status') or 'confirmed'
        msg = t.get('MessageText') or ''
        type_ = t.get('TransactionType') or 'other'
        sql_inserts.append(
            f"INSERT INTO Transaction (TransactionID, TransactionType, Amount, Currency, DateTime, ReferenceNumber, BalanceAfterTransaction, Status, MessageText, CategoryID) "
            f"VALUES ({t['TransactionID']}, '{type_}', {amt}, '{curr}', {dt}, {ref}, {balance_str}, '{st}', '{msg}', 1);"
        )
    sql_inserts.append('')

    # Insert TransactionParticipants
    sql_inserts.append('-- Insert Transaction Participants')
    for p in transaction_participants:
        sql_inserts.append(f"INSERT INTO TransactionParticipant (ParticipantID, TransactionID, UserID, Role) VALUES ({p['ParticipantID']}, {p['TransactionID']}, {p['UserID']}, '{p['Role']}');")

    # Return insert as a string
    return '\n'.join(sql_inserts)

# Main Usage
if __name__ == '__main__':
    file_path = 'data/raw/momo.xml' 
    sql_output = xml_to_sql(file_path)
    print(sql_output)
