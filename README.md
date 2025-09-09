# MoMo SMS Processing Application

## Overview
This repository contains an enterprise-level full-stack application (coming soon) for processing Mobile Money (MoMo) SMS data.  
The system ingests SMS data in XML format, performs data cleaning and categorization, persists the results in a relational database, and provides a frontend dashboard for analytics and visualization.

---

## Table of Contents
- [Features](#features)
- [Repository Structure](#repository-structure)
- [Architecture](#architecture)
- [Development Workflow](#development-workflow)
- [Team](#team) 
- [Setup Instructions](#setup-instructions)
- [Contributing](#contributing)
- [License](#license)

---

## Features
- XML parsing using `lxml` / `ElementTree`  
- Data cleaning and normalization (dates, amounts, phone numbers)  
- Transaction categorization (payments, withdrawals, transfers, etc.)  
- Relational database persistence (SQLite, PostgreSQL supported)  
- JSON export for dashboard analytics  
- Frontend visualization (charts, tables, trends)  
- Modular ETL pipeline (`parse` → `clean` → `categorize` → `load` → `export`)  
- Unit tests for core ETL stages

---

## Repository Structure
```
MoMo_Enterprise/
├── README.md                         # Setup, run, overview
├── CONTRIBUTING.md                   # PRs, branching, and issues guide
├── create_environment.py             # Script to set up the application environment
├── .gitignore                        # Files that Git should ignore
├── .env                              # DATABASE_URL or path to SQLite
├── requirements.txt                  # lxml/ElementTree, dateutil, FastAPI
├── index.html                        # Dashboard entry (static)
├── web/
│   ├── styles.css                    # Dashboard styling
│   ├── chart_handler.js              # Fetch + render charts/tables
│   └── assets/                       # Images/icons
│       └── architecture              # Architecture diagram
├── data/
│   ├── raw/                          # Provided XML input (git-ignored)
│   │   └── momo.xml
│   ├── processed/                    # Cleaned/derived outputs for frontend
│   │   └── dashboard.json            # Aggregates the dashboard reads
│   ├── db                            # SQLite DB file
│   └── logs/
│       ├── etl.log                   # Structured ETL logs
│       └── dead_letter/              # Unparsed/ignored XML snippets
├── etl/
│   ├── __init__.py
│   ├── config.py                     # File paths, thresholds, categories
│   ├── parse_xml.py                  # XML parsing (ElementTree/lxml)
│   ├── clean_normalize.py            # Amounts, dates, phone normalization
│   ├── categorize.py                 # Rules for transaction types
│   ├── load_db.py                    # Create tables + upsert to SQLite
│   └── run.py                        # CLI: parse -> clean -> categorize -> load -> export JSON
├── api/                              # Optional (bonus API)
│   ├── __init__.py
│   ├── app.py                        # FastAPI app with /transactions, /analytics
│   ├── db.py                         # SQLite connection helpers
│   └── schemas.py                    # Pydantic response models
├── scripts/
│   ├── run_etl.sh                    # python etl/run.py --xml data/raw/momo.xml
│   ├── export_json.sh                # Rebuild data/processed/dashboard.json
│   └── serve_frontend.sh             # python -m http.server 8000 (or Flask static)
└── tests/
    ├── test_parse_xml.py             # Unit tests
    ├── test_clean_normalize.py
    └── test_categorize.py
```

---

## Architecture
The system follows a modular design using [draw.io](#https://app.diagrams.net/):  
- **Data Ingestion:** SMS XML input loaded into ETL pipeline  
- **Processing:** parsing, cleaning, normalization, categorization  
- **Persistence:** relational database + caching layer  
- **Export:** JSON aggregates for frontend visualization  
- **Frontend:** static dashboard consuming processed data  

[View Architecture](#https://viewer.diagrams.net/?tags=%7B%7D&lightbox=1&highlight=0000ff&edit=https%3A%2F%2Fapp.diagrams.net%2F%3Flibs%3Dgeneral%3Bflowchart%23G1r6y-ivDrfy5aN0oYS-Y4Q35_Gp_AdRhj%23%257B%2522pageId%2522%253A%2522C5RBs43oDa-KdzZeNtuy%2522%257D&layers=1&nav=1&title=MoMo%20SMS%20Enterprise%20Architecture.drawio&dark=auto#R%3Cmxfile%3E%3Cdiagram%20id%3D%22C5RBs43oDa-KdzZeNtuy%22%20name%3D%22Page-1%22%3E7V1bd9q4Fv41rNU%2BhOX75ZFw6cxpk8kk6XTmKcuAAz4lmDGmac6vP5JtGVuSsWQk41DoWiUIWxZbn7b2XT19%2BPLzU%2BRtljfh3F%2F1NGX%2Bs6ePepqmKoqjg3fY9JY2mY7qpi2LKJhnl%2B0bHoL%2F%2BejerHUXzP1t6cI4DFdxsCk3zsL12p%2FFpTYvisLX8mXP4ar81I238ImGh5m3Ilu%2FBfN4mbY6mr1v%2F80PFkv0ZNXKft%2FUm31fROFunT1vBS%2B6mnvR9w89TZ8kr542zP%2F%2BmN724qFnZATYLr15%2BFpo0sc9fRiFYZz%2B9fJz6K8g1RE5v%2F3%2B9m315bv16T9%2Fbv%2F1vl5%2Ffrz96yrtbMJzS%2F7LI38dN%2B76%2Buv9art5%2B%2FO%2FprmI7paflO9fZ1eqkxHph7faZYTOfm38higPibfp6dfPwWo1DFdhBJrriahfLyJvHoAh89yzjaPwu89zByNxyuj0pujHZZP7w49i%2F2cBaRkRP%2Fnhix9Hb%2BCS7FvXsdJbsoV05aIV8rqHpaZaWeOygEnNRa1ethgWeff7mQN%2FZJPHM5G2Uj%2BRy%2FgFdDpSAdXm3nbpww4V8OF1GcT%2Bw8abweteAQNhn2x3oqfT8BzuJxp88Zy8iAkF31gTBbyoE1cD0fopOuUMODb7SvIARdeQsP5z3IASx4PY0NwSiE2NxLCpUgiou7LoZ9DoZ60gfebBjxIdrX93kOlegx8bX2W0HIArcnKiC8Bfi%2Bw96Wi78dbUnvZ7xNUshSrsL4689RZNyzVswB44A9%2F40cFHwnVBfWThOYX1FS2mH5RkbSno7WP6Tvvm48FHTyO8BUxMOh6iOaUM0ZxQvtx6mYzLZFwm4zIZv8pkVFKmwfyJI6YiBQreC5RO1tPtJr27w00pdOiTlbZ9qYcTcX8FxE65OlpiBOEhsrQ1CG8OvgfSsbee%2BVHNPFVMaUVziUNgUnnyEw4qQwXFqVovUq8H6lhL9aKxxa0XKYo1Hkx6hHIAhP3YC9aQYiMOtSlXR7i0ppZlflXRWZUmvl8tQENSSgqSrhP6kaEbfWR9KpErt3oJJ5daT63t0tvAP19%2BLqAlsL%2F249cw%2Br7V%2BgEgCoTXdpOa556DnxD0BxCtJK8U0enfpIlmfxlp8AHfmdeWaumQeafj0H4Ho3hAljS18MV0MSkMZB2uwa%2B4XnlTf3UXboM4gIMf5bwDTmQw81ZfsAumYRyHL4VVRNwxyL6Iww02LCrVFqtw6mMXfsOGDtt%2By9qKy1VlX677lVCP0AySlkWq7BoJR9RGQ2PW9z1cKusFgFAO%2FytTKS8AZF8qPo3CKwyMVXgrQP21F%2FvXkMluiSWQ%2F6zmqwINg2I4yPeN0e0DfTs5Zis4ZKukLx24GWSWdY3HBKYyYyM3%2BJcmT3X7JjF9iKUVp0%2FVZbEuTTbrgrvuCP775VjUbBXu5tiF%2F%2Fzx%2FLz1Ia2ulL7i0BhYH1DEoHAxpW9rEFsyWFf2rW6ZJXxaNoFOy6VurqYsUcSk7a010j%2F84mqbrGco2AJa%2FayT5dOG4eiWS7ptl0tJnHfbKc27S3Ilg7KFqdLkTwabvT9f%2BA%2FZxzCKl%2BEiXHur8b71ujwd%2B2u%2BhHD9JpPwXz%2BO3zLO7%2B3ikGeK1NH1cD9FRTcZ8oM2WazbcBfN%2FANXZqSJvWjhH%2Bwx6xDS6SAGIn%2FlxcGPsjtX%2BJRqDBpFC1Pq%2Fwziv1Muq7rZ538S5mooZvZ59DPrP%2FnwVvhw50cBIEeu84E5jd7%2BTm5XEtacNKT96ZaLGvYdJp%2Feip%2FwLk%2BBOXEQyW69C4OENWfsBYjEfUV396%2Byp9Zx%2B7qp7F%2BYYJyuiKzLoiMde4pu6X3XUmyD6NxWHAd1bpU7T5cR0bkoGbjad9aC6UrB90GDdR%2F8uoVmHmXk%2FwgAL%2BK391DsvqTtimZepj2gyojcbv8nmC9VZZ2vb%2F70agpDeRLrnBhz7k04DVb%2BlbfZNDP4sVn21HpBiTe8hZ2DWtZwWG8LPIaz8miGmOitEiIYNXLCliWDMQQg0fWiWv2qUjMjFK8CCsJdvArWYFpRFJtC6pnPJvxH0zOt5FXQM0dBBLpJn7%2BGcgR1uqs03%2F7K26Q%2FlqK3TpN%2FcsGil8HikmAxKFjR5NmL3x9YLMO2HJsGFl01dNMQB5aXhJMe4DPygAIUc0waIrmKgmxQJaiYsqDidEMP2EvuZklur5HZO6kSIlWvXic0OqUTqgw6YS2DKEwqncUQjKI8h5m58JC35Xo80dJpha9sWrHV7v1vF%2Fnp%2F0%2Br0Js%2FTZG7tE2pQbXJnYDFHSBuSg1%2Bjaexue6EYQBA4u7t4x0qpOATjOvBjwB6ts1CLBhVOXETSVPRWNSJai2Q1uNZaiJ5oLgkZ2YFg9HMU%2BslGoOz%2FZ3YhpExUulbutPbGyOhayhvaGSNzPrbWyNdNzdP8lgjxYsqBqOoYouWVCpMk0gGQRuojnXBan3UMJVMtbCOJFsaNdrGe2BZZGJPA%2BSXl06O4V7JmK653PDtpGjNCsOSQpWxviOhadB1fF5gmoe7qYDlIIq8t8JlG3iBlDARmzk%2Fh3Nuj481U%2FVyuIbmUDY%2FamSeIUu8NmvEa5b4UFIgG%2BziJaAq0J0S7UqIC7xleWqYvNI7DAv%2Bk2LZzdHKFb5JBQlycgsHiW3xgiRtuPdiGGn2JXgBSvZ6cYGBEBi8lWf7dKggDW%2Fj0adxr%2BD5Sf8nfUM12RPMqRt39%2BOH8e3j4JEGx9%2FrdUBaCgCdxTXMJknb%2FmigPR9PnNvKH4qtLdgjsQoycY6wdT2TgXEHDGYvwXyeqEe0FVuW%2B4pLijPEUkf3I1mUkkgvzABOGrx1m7ZjC1BXqfnt5Kq7DQ%2BwS6U8QRRJnCqxF6irpubt%2BQDWdgCfp6tw9j1tglGSubaHSkk4BB9M1FsUZwkvTnww13lWCYanemWbdXqRd6JW2s4mV%2BlDe2xZRDtS9kaXhGmY5iHBGqCxHGriGpjYxyqiEz2pMAK0Te2RJlZiGBVTpKCYjDMBatzEaZaMwwspdo7hKOUUfJuWgk9lIdLScWyaL57ct64Hw8%2Fj21H9jj64A5ut8jC%2B%2F%2Bv34fihcrdrsO9ku9t57ToNMOSU17NtGgSGDE3SNkT9EQyeNjELfKApCnQepyL7%2BHp83ZkqJBU1NlSXkkOjqjS3mbyIZ51m1T5dpCCzC%2B7hBvAP5RPQHF%2BhvahjGuM4c6uwxtpPJq6r68eZFvkBqZo2hkjdpCCSxi%2FkpV1wmpM742XZ%2B1RQOPc%2FvX3od4U1Onec9EpOkzwy5GAwyDEgEecvQQE7sh0mlq73MU%2BHZjeUe10Vw72KG065rdMVgzYJ%2BVo5ODLbco%2B7wTFK14M%2F0jELldqRwCnMdC6wkBVOQN0iWZpBE6MN3AMnToxm0HJ4yIXIfwS1qoN9qbTRpXnVVYWB4fMQBxH7eChdGWrfLr7KuWr5NJTKJZRvcSgwkxYMy0BIMaK2PRioqpVbx42RzpUlaDBPRFcoa3cjh4yXwrWbvO4ybvKotEBH4jfRuN%2Bb0jL0ZkteB9fR0XCqlQ1PaUIC6HCCf%2B%2Ff6%2BsTpQ0f7v15sP0oIInn%2FZJgBJ9JGMWUAVj1b3EwA5KjAjHhi6BSC3ptXtyVVa91XWNYLBLTKGSGfb9A3xpWXyu%2ByqZ6nVafV3H7lqUe2l6kiUCo2MG57S6Wxri7IHbekd3FYsgU4QsMMkSJpIclUlcjcK06NFe%2FtCh8lAVwmtx6HtMLexUMyzqSgyE8MS8Y6bGnitN3Cq%2ByxqyhTCnBthBH75vFVzkXX82wXBnmenDM2N1yrB5oeqoKUh9dJpQ7v6GROMNZbjJiF0fYZbkzIc75%2FjI5036h19H0IrSDSmowVmOVR5v7ZJeCO3nNj%2B%2FuT8ADGEYM80jT3ygTyYcP%2BdWru6Iy34XbeBH5D39%2BSVRnoHoqN2%2Fg00VFrldY%2BGLD21UNTIa6HtvvfjxbIkWAWkuhHM8B%2Fk3gGIhyGAzJ1fWlbLNOSpby2rRwxlzwIrIKMZRarxwrBB9JVLlMJG0%2FGv%2FwocCdx02W08Jft0Y%2FCOMnD9manuZe7D1t4zCCP6phWVoOqCEXqNY3bMfav8qCO8U5Rws3sPu2IwmY9kmsLSL0z4LeqyBtlyHogJICJ1yTFe4vkKnJkhXdTLOvFl%2BYF9%2FE%2Bq2IO%2BDVkHVYQLzabvkeVGTm0%2BNaN51pLmBExVeZEVGcuapl9W3N2HMuilFY3n5pVSdTnbEaxaRXcYh%2Fv5xJgqDNGf%2FUi42iW%2FQqujVHQNgEb98Ah1%2BiS488xoo4oWa3LdYIZT8K6hgWcq4qZKMzNU%2B8QzJEISK1KHhJThOuL9rFVheQzEmrnk%2FL0vV0dpJBDJA2R1XtsnGOlnEMj1EeJAaQCTzuYNufBx7Q7V62sMBf1ng1g9EDYKIm17st0Oa226enp0mwhgXAnhart83y6S%2FzCqhUQJiYqIb%2B5O3mQfyUL9SnKbotUQ5fwPB9mIL9tAFki54ifwNUG6Ahuf3tj0UPy84jk%2FeS0V8Xj1fOVGjxKEQOUafvOgWhTqvTLi2z72gkSgvN4g%2BCpfmTySyq0eBxwMp2ftWUKJdb7FctjXLUiUOpPCktBUqrK4vQ0Wi1R7j%2Femn9UU2BBd54i3LL3yyHQ7aaZ0VAgu1y1HaqjYMirfNQjVMn2ug1%2BiWXuEtAoY0TLytF6Wbi5A3YBuHmqyl%2F7vwdfE%2B9D4mZFbyDHbZXqrxIEzgFi7gyvDYatKkME4Lt%2Fyj6bjI679%2Br%2FHvedBrEN3%2BCa2Ba72fv%2BbtXL05zUa27aOlVFCupVkRo7LJl79R75ZaqQmGXGi1I05LFLlEFrg6mPLlamVoOzalCK%2FkjMavYJojT0TjAQu1Kw8JqVyp673AeZoODdMqScTFLWGo6J5JB62Nx5XhueF0hOKbdTPKvzOh0D14vx9uBSsCcCuWajHBXBErs1AJFcTyFnnvctKS9eJCbjCDXWnJPEijGGa6g0FpVweDv2IeXC3lDdvJe5frC95jy9ZLSjM1TrC%2FBnvkmO9Fpl5HOule0Fa9umpgrW2dcRySM8YIXxNE0Fa58UZBWlfdQRVxo%2BgN7dbUjYWK7%2BOTixhPW%2BhBET0RqsSDGTTxIt1uQW1SmY073lfxmK2%2B7DWYJCLwoJpsri3SLkIUJQcRUfJ7Di5jhV3N0CWo7FqVYvXYL%2BSy4QVrXkSiMGvTn8I5LKqSN91rGyp%2FtoiDmq2AlMlCBHi%2FCYGnUan6iULJXxpMTR1daFcP6gJcap6RlTyJvNwfvNzWUFxkP0kp0faV9tdJ83DAiYx3ETU29oocSlQstVBhladMr1BpdjVzG5BZWgH9s9mNPEgR1IhbQdN6n4U%2FYPwRU8oRpGM396Ao0pwN4ARttkCXg5G6FjTef53fkreLydU5Dw%2FF6Fr1t4qApKQWv8tOy12Qbga6v%2B%2BvBMPtz2MwDVtH8i2wbL8I3jcp11nCIm6YjFMzlVwEM7WrM6vnY3nFDl5s4yLDdHR352fr5faPByOYrGwuDLlsvG6vpZatFGiuAu2ddig4tsYxg9QFFxIx3SSMcgk1jMhw11ThOqMPyCYRVwRJcHIlZetoUBRQufs3%2BCB9mpzbmxAQoj8r1Pw0P%2FvApiH%2FbgVEqg9k5iISUH95EKmwmAR5bBOE0EFhvM7n3P%2F76e7CuO%2F%2F3WFnjNEoPg6xBkyraFh9GsO48j%2FgATywT5dxhFx9s3WGQHpJ6fK0KECeN0mY2zx7DWiu39BtouMssZhS76JdwsWhsTTsqg%2FM9boqXfTAdwF3UbCM8xR6RHFYLPxT%2F4N0mTk5xyAqX%2Fu5Xkj%2BQ%2BPEp8p69tZd9Gk8%2BXwSRiyBSFzdts5gxUFpYS1IILTKjsQPmeC23AyLQ0dINITkM89pHmvJHNFv6AHUsB1DzafgcV5%2BhmPM%2Bt5PPu6kfrf3Yvyiyl%2F2D96gh%2Bv5BK2cmb%2F%2FQyP3j99vJ%2FeDh8f7r8PHr%2FZiYwF%2F4VOcGIoNmYFOu0GwXlCmXll2uolMluxlA7Lrl2oq0KPli7bp9xDzPkXlqr%2BUYeRRvKDummcgbN9xyF6yR76qp4dwKnRUruIqdamFBzRpyzlWODb9DdbKI%2F8pSd8fegOgoN85aZzk3ah9nTXLU8jKtyhCpQz%2B58vjD%2F3lXUG3ySK7qdCQu28SLR%2BqMqSFkkgmWrrJ3hbd0qHp%2BmuUFdwciBTqCO8fQBeHOJPgunv%2FCnREgHpkMR2GeKTI7gjdVcUUBjuyKKPbWAcRZJMC6Ix6%2Fp%2Fw6VVOwJGBcqWEVRsm9VtWZIMgri1Zu6pWQdtRj70BUkStaGoLPFBZYjwSwBUw6N9Hgiloy7fgBiWoyyo47RLDysm9szCou8JE9dFNjFutE5DPLVYqzdXIyiJhc%2BDOEndusuX27nIKIyFCkl%2Br2KUUAVWkFhFS9rgxkt8I7c0Pw9eD280MvP4tlfD%2F8bXD7uG%2B5H3%2F6%2BmXwKM7n9EeFlfr%2BgSuCpHJtn7BS77VmWcU7mmz3%2BcpjZ8hmXysvCJNcECotXluVViFKNWi2ETLGafz34%2Fj%2BdgAPA7r7MvhnXALBOddI1fKjYXjN2hwAqWeI0nYQ1PF7Y4eP%2FsqfwYwl5daPX8Poe9eY0mRsFUspsGSRuK6ut55FYuK1WCyK%2B6zlmqg0GfEdYPLrwwMYkfLJi%2F1Xj6%2BWwAWQ1YA0KYUU2wVkfvLQu6jUwjs3XbGImTp20FKuTHFbxOq7ElXyzTQqnsQ%2FNsnFhvhMvhcIC4GwiVtim0OY6EoahNGT%2BMcmGcK03JALhCVDOI8KOB7CRFfSIIyexD82uRBGiO0MhA8FBr1TCBNRKbru9N3Cy2yGZ95%2BBYGbfKxl9C19%2F0%2FEoOWiXkEHlnbU%2BdciFz%2Fe%2BVcOfXRMNtSRPRmobmx%2BMqnCJqtwc2f8SWjMcquCs6hs5wlCgRW6HSmw5i%2BsjcVf1hfWPnyDJMidpFD2vsi1Lb%2FK9TEROwjgJ4SzHC7dvTrxqobibdosFK9VF%2F%2FptN12cJfkriKzbeZQHT%2FUJeRcTlmrSM9wMLRSDLgaCtdp5dgg%2FSQCaJPjB85RaMVPhVEVJItxC62KVVbbXRvrSZTMSjyo9uQb7ajrc5rI5dDvNPileKT15QTMo9xrChY9evojMJFU9t5A%2BXWbpK7feGtv4b%2Bkp1M2AWcrtZ4b%2FEoxD25wi9Tc8sFsVl80gLVaYMWldOI1S7nfn5BZuIlKi%2B7RGvzWuC6Fn4OsvctJnVVcXTUYuDottBD3iwuMLKSx9WpXR12OkQjBmJ61rPStGqsH9YBJ3tmsP%2FNRYxTHW%2FIEEgbiI5zZdl1XsnMxEVEuaGRFo9I1NGJKJKu7goZGpdwVq19aHBpZjp87FRrlnnvYWTw1jzazsM1X1Y%2FO%2BK16kloxaPaxtRNtZvKVXLiE6gjZoFVVSKADd8ei4E0%2B1%2BAIdWAdtmTkv6c4yzM71NG0y0ZbC%2BXgcNdwqOtIEOJNi%2F4c3nFJhjTNanxaSLeYrt9WPQgFE0pVp8T70GHp%2FNUhODsWdhg68VyzzI2FDFsy8vlsGJdwzSbIJ8qOuZYhRIzh7ViYlE4811U4xBjGYctFvsVnL7kgv4lf3NH6WGWUvIIef7kzls4EIdx1q5%2FVZHySocxnbLmIL43EF7wGlWaWVbemTJy3Y2HiC%2FFcrU5iYRupZLBrF7DLBjtRK1AzTRFY5%2B1XENTJx%2BqHjYqM45QM9O5ZGM8O6ETdNs20RQCdt19R1hbisZnL9chxSgZ692oPnB3QieqBqu6qfUOADsrbsSjxhXiuodp9lVkHZRy2ZOR3z5R%2Bfsg3bKXvOJhVTkBRWs5%2BxbmQWB575Kglw77jpXIPxBA0SHjgXTe12WB5hUf5h0KULdSu1TQVV8UDUkyXzXHFvTzwM%2BNVuyaTTNeVI29QaqqJOPiQeG9AdJe8KrvnBDu7iAYCO7ruivAE8PYraDMiH2uZ7H4AxkFLRn3XHGBniHqaZdxuCnWmziS6Aeq2h0Pjkwtlm%2BYG4MuaMWm5GILP2%2Fw8%2FkdgptAJfkCeBBM1TOvg%2F5XyssH0A3lS6cHs6%2Bk2O59dctO9%2F%2B%2FO30ICTFaAq7b%2B%2FK42jbzYuxCl2PTgz3ZREENWPl4%2Fh2DfSLMTTz2ud9Q0CSL%2F1YO7yjEZaQVpZ%2B5tlwePtOCtdV%2BsaQ6%2BeE5evcOClDXZC1LpC%2FaEVWHnlaJ4ToTA7Ckm0qCLWWom7ajWvOyV%2BDw1u3uOpLMTcXXb7iuFFyrOhYBga0Aq1Boqdw36FqXgKRr%2BrBqdjn2skoXhi1NJOuht2y1PNj7XamPMN%2BhaEORthYSsoKFKRnzXnElnGNCY5OsUJ9usnGx%2Bh1KDvoXFguFHzNeBnmOwklHPZ7UWn2iay73qWQHdwkOg0M7fJEq9rithcelaxZOqx2YdvkMWahtUBMIMN06V4eYmvAnB9x9uwmkAutCUG4D5t4%2B4Ajhex360iYItvGQQzaDGNot3kV%2BpEWKr6p2fe6Wj%2B7nPvWqgF2LFKjV0VkVRLbRpJyvKO1gRPa3mXLSR%2F%2BOPzbZoQEj%2FT3EVxGEUrBcXyIgveIOisfeheQ5pS9BppgSJmKnzMFwww4AZ2HsMNucQjuLKVaWapFQLd0YZlMpJbeNIY8JRwcz7xXtLatF98HbxEhAJTGQcVEAoXFOh9xx5uzl4n%2FtwowPU%2F%2FgLYE0armwFT3WinKpnq%2B3Ciu2ozwusRLMwRSoLu8Kr6xqUcsttQ62uEniKmbvddBVsl%2BDC8Q8%2F0V2UD9sX%2BLYO4%2BA5gVu43n6kIusBbJR%2BD1Xr%2FnPnJ0RJvYG%2F6t4pDWQmVjVWRakTZYW7XZCRx4HtfeQbL14m7Cc5I%2Fbm8Tb18w8C8ItX6d8P3rMXBckhsvBjenrnkI61m4dfAD2tsi1VUay%2BiYHKUvqk6pcfcdMSrGwCVnfeW1bf996f%2BcEGcioIlG9BvJxH3qu32lYh5xGWd332o%2B0FP4Lwk29zyum3OdK6eoEKP1TkMhrDxEVxicABH6MQ2hv39lBAzOVNOPfhFf8H%3C%2Fdiagram%3E%3C%2Fmxfile%3E), on web or locally in architecture file in web/assets/.

---

## Development Workflow
We follow Agile Scrum workflows using a shared Jira Scrum board.  
Columns include: To Do, In Progress, Done.  
Tasks cover ETL modules, database integration, frontend dashboard, and CI/CD automation.

[View Scrum Board](#)

---

## Team
Team Name: [Team 1]
Monica Dhieu [Github](#https://github.com/m-dhieu) – Backend & ETL Pipeline Lead
Janviere Munezero [Github](#https://github.com/Janviere-dev) – Database & API Integration
Thierry Gabin [Github](#https://github.com/tgabin1) – Frontend & Data Visualization
Santhiana Kaze [Github](#https://github.com/ksanthiana) – DevOps & Monitoring

---

## Setup & Run

Prerequisites and instructions will be updated once ETL and frontend components are implemented.

---

## Contributing  
For contributions, view the CONTRIBUTING.md file to guide PRs, branching, and issues.

---

## License
This project is licensed under the MIT License.

---

## Contact Information

For any queries or feedback, reach out to any team member.

---

*Tuesday, September 9, 2025*
