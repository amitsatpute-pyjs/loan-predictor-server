def response(res, loan_amount, gross_monthly_income, rate_of_interest, loan_term, Total_Monthly_Debt_Payments):
    emi_value = loan_amount * rate_of_interest * \
        (1 + rate_of_interest) ^ loan_term // ((1 + rate_of_interest) ^ loan_term - 1)
    if res['loan_status'] == 1:
        res['reason'] = []
        if res['cibil'] < 500:
            res['reason'].append(
                "Your Cibil Score is low. Please refer the link 'https://www.bajajfinserv.in/insights/7-guaranteed-ways-to-boost-your-cibil-score' if you want to improve Cibil Score.")
        if res['loan_term'] < 5:
            res['reason'].append(
                "Sorry!, Bank doesn't provide loan for less than 5 year")
        if res['anual_income'] < loan_amount:
            if Total_Monthly_Debt_Payments:
                dti_ration = Total_Monthly_Debt_Payments / gross_monthly_income
                aaproved_loan_amount = res['anual_income'] * dti_ration
                if aaproved_loan_amount < loan_amount:
                    res['reason'].append(
                        "Sorry!, Bank can approve only Rs" + str(aaproved_loan_amount))
            else:
                res['reason'].append(
                    "Sorry your Salary is not sufficient for getting Loan")
        if res['bankbalance'] < emi_value:
            res['reason'].append(
                "Sorry!, Your bank asset Value is less than the monthly EMI")
    return res['reason']
