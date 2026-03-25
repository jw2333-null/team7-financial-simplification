# Data Collection Log

This log records every source document used in the dataset. All sources are publicly available consumer-facing financial documents.

## Source A: Financial Institution Documents

| # | Source Name | Document Title | URL | Access Date | Format | Local File | Issues |
|---|------------|---------------|-----|-------------|--------|------------|--------|
| 1 | Bank of Scotland | Credit Card General Terms and Conditions | https://www.bankofscotland.co.uk/assets/pdf/credit-cards/terms-and-conditions/general-terms-and-conditions.pdf | 25/3/2026 | PDF | data/raw/financial_institution/bank_of_scotland_cc_tandc.txt | |
| 2 | HSBC UK | Personal Loan Terms and Conditions | https://www.hsbc.co.uk/content/dam/hsbc/gb/pdf/loans/personal-loan-tandc.pdf | 25/3/2026 | PDF | data/raw/financial_institution/hsbc_personal_loan_tandc.txt | |
| 3 | HSBC UK | Credit Card Terms and Conditions (Oct 2018) | https://www.hsbc.co.uk/content/dam/hsbc/gb/pdf/credit-cards/HSBC_Credit_Card_Terms_and_ConditionsOct2018.pdf | 25/3/2026 | PDF | data/raw/financial_institution/hsbc_credit_card_tandc.txt | 25/3/2026 |
| 4 | HSBC UK | Classic Credit Card Summary Box | https://www.hsbc.co.uk/content/dam/hsbc/gb/pdf/credit-cards/summary-box-classic-credit-card.pdf | | PDF | data/raw/financial_institution/hsbc_summary_box.txt | 25/3/2026 |
| 5 | Barclaycard | Terms and Conditions (general) | https://www.barclaycard.co.uk/files/Terms-and-conditions-barclaycard.pdf | 25/3/2026 | PDF | data/raw/financial_institution/barclaycard_general_tandc.txt | |
| 6 | Barclaycard | Amazon Barclaycard Terms and Conditions | https://www.barclaycard.co.uk/content/dam/barclaycard/documents/personal/existing-customers/terms-and-conditions-amazon-barclaycard.pdf | 25/3/2026 | PDF | data/raw/financial_institution/amazon_barclaycard_tandc.txt | |
| 7 | Nationwide | Our Savings Terms and Conditions | https://www.nationwide.co.uk/-/assets/nationwidecouk/documents/savings/terms-and-conditions/p3780-our-savings-terms-and-conditions.pdf | 25/3/2026 | PDF | data/raw/financial_institution/nationwide_savings_tandc.txt | |
| 8 | Nationwide | General Mortgage Conditions 2019 | https://www.nationwide.co.uk/-/assets/nationwidecouk/documents/about/information-for-lawyers/forms-and-downloads/m139a-general-mortgage-conditions.pdf | 25/3/2026 | PDF | data/raw/financial_institution/nationwide_mortgage_conditions.txt | |
| 9 | Nationwide | Current Account Important Information | https://www.nationwide.co.uk/-/assets/nationwidecouk/documents/current-accounts/resources/p4055-current-account-important-information.pdf | 25/3/2026 | PDF | data/raw/financial_institution/nationwide_current_account_tandc.txt | |

## Source B: Regulatory Consumer Guidance Documents

| # | Source Name | Document Title | URL | Access Date | Format | Local File | Issues |
|---|------------|---------------|-----|-------------|--------|------------|--------|
| 1 | FCA (UK) | FCA Strategy for Consumer Lending — Portfolio Letter | https://www.fca.org.uk/publication/correspondence/portfolio-letter-fca-strategy-for-consumer-lending.pdf | 25/3/2026 | PDF | data/raw/regulatory_guidance/fca_consumer_lending_strategy.txt | |
| 2 | FCA (UK) | Being Regulated by the FCA: Guide for Consumer Credit Firms | https://www.fca.org.uk/publication/finalised-guidance/consumer-credit-being-regulated-guide.pdf | 25/3/2026 | PDF | data/raw/regulatory_guidance/fca_consumer_credit_guide.txt | |
| 3 | SEC (US) | Investor Bulletin: Interest Rate Risk | https://www.sec.gov/files/ib_interestraterisk.pdf | 25/3/2026 | PDF | data/raw/regulatory_guidance/sec_interest_rate_risk.txt | |
| 4 | CFPB (US) | Getting a Credit Card and Using It Wisely | https://files.consumerfinance.gov/f/documents/cfpb_building_block_activities_getting-credit-card-using-wisely_guide.pdf | 25/3/2026 | PDF | data/raw/regulatory_guidance/cfpb_credit_card_guide.txt | |
| 5 | CFPB (US) | Differentiating Between Secured and Unsecured Loans | https://files.consumerfinance.gov/f/documents/cfpb_building_block_activities_differentiating-secured-unsecured-loans_guide.pdf | 25/3/2026 | PDF | data/raw/regulatory_guidance/cfpb_secured_unsecured_loans.txt | |
| 6 | CFPB (US) | Consumer Advisory: Credit Repair and Credit Reports | https://files.consumerfinance.gov/f/documents/092016_cfpb_ConsumerAdvisory.pdf | 25/3/2026 | PDF | data/raw/regulatory_guidance/cfpb_consumer_advisory.txt | |

## Notes

- All PDFs were downloaded manually via browser (Save As) and text was extracted using pdftotext / PyPDF2 / manual copy-paste.
- PDFs are NOT stored in this repository (see .gitignore). To reproduce, download from the URLs above.
- All documents are publicly available consumer-facing disclosures or regulatory guidance.
- UK regulatory content (FCA) is available under Crown copyright for educational use with attribution.
- US federal agency content (SEC, CFPB) is public domain.
