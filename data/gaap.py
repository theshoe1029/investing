US_GAAP_TAGS = {
    'Revenue': [
        'Revenues',
        'SalesRevenueNet',
        'RevenueFromContractWithCustomerExcludingAssessedTax',
        'OtherIncome'
    ],
    'COGS': [
        'CostOfRevenue',
        'CostOfGoodsAndServicesSold',
        'CostOfGoodsSold',
        'CostOfGoodsAndServiceExcludingDepreciationDepletionAndAmortization',
        'FuelCosts1',
        'MerchandiseCosts',
        'StoreOperatingExpenses',
        'CostOfSalesAndRelatedBuyingAndOccupancyCosts'
    ],
    'SG&A': [
        'SellingGeneralAndAdministrativeExpense'
    ],
    'Gross Profit': [
        'GrossProfit'
    ],
    'Operating Expenses': [
        'OperatingExpenses',
        'CostsAndExpenses'
    ],
    'Taxes': [
        'IncomeTaxExpenseBenefit'
    ],
    'Other Income Loss': [
        'NetIncomeLossAttributableToNoncontrollingInterest'
    ],
    'Shares': [
        'WeightedAverageNumberOfDilutedSharesOutstanding'
    ],
    'EPS': [
        'EarningsPerShareDiluted'
    ],
    'Operating Income': [
        'ProfitLoss',
        'OperatingIncomeLoss'
    ],
    'Pretax Income': [
        'IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest',
        'IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments'
    ],
    'Income': [
        'NetIncomeLoss'
    ]
}

BASE_GAAP_TAGS = {
    'us-gaap:Revenues'.lower(): 'Revenue',
    'us-gaap:SalesRevenueNet'.lower(): 'Revenue',
    'us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax'.lower(): 'Revenue',
    'us-gaap:CostOfGoodsAndServicesSold'.lower(): 'COGS',
    'us-gaap:GrossProfit'.lower(): 'Gross Profit',
    'us-gaap:ResearchAndDevelopmentExpense'.lower(): 'R&D',
    'us-gaap:SellingGeneralAndAdministrativeExpense'.lower(): 'SG&A',
    'us-gaap:OperatingExpenses'.lower(): 'Operating Expenses',
    'us-gaap:costsandexpenses': 'Operating Expenses',
    'us-gaap:NonoperatingIncomeExpense'.lower(): 'Interest Income',
    'us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxes'.lower(): 'Pretax Income',
    'us-gaap:IncomeTaxExpenseBenefit'.lower(): 'Taxes',
    'us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding'.lower(): 'Shares',
    'us-gaap:EarningsPerShareDiluted'.lower(): 'EPS',
    'us-gaap:marketingexpense': 'Sales and Marketing',
    'us-gaap:generalandadministrativeexpense': 'General Administrative',
    'us-gaap:otheroperatingincomeexpensenet': 'Other Operating Expenses (Income) Net',
    'us-gaap:operatingincomeloss': 'Operating Income',
    'us-gaap:investmentincomeinterest': 'Interest Income',
    'us-gaap:interestexpense': 'Interest Expense',
    'us-gaap:othernonoperatingincomeexpense': 'Other Income (Expense) Net',
    'us-gaap:nonoperatingincomeexpense': 'Total Non-Operating Income (Expense)',
    'us-gaap:incomelossfromcontinuingoperationsbeforeincometaxesminorityinterestandincomelossfromequityme': 'Pretax Income',
    'us-gaap:incometaxexpensebenefit': 'Taxes',
    'us-gaap:incomelossfromequitymethodinvestments': 'Equity-method investment activity, net of tax',
    'us-gaap:netincomeloss': 'Net income',
}