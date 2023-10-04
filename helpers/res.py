def response(res, loan_amount, gross_monthly_income, rate_of_interest, loan_term, Total_Monthly_Debt_Payments):
    emi_value = int(loan_amount) * int(rate_of_interest) * \
        (1 + int(rate_of_interest)) ^ loan_term // ((1 + rate_of_interest) ^ loan_term - 1)
    if res['loan_status'] == 1:
        res['reason'] = []
        if int(res['cibil']) < 500:
            res['reason'].append(
                "Your Cibil Score is low. Please refer the link 'https://www.bajajfinserv.in/insights/7-guaranteed-ways-to-boost-your-cibil-score' if you want to improve Cibil Score.")
        if int(res['loanTerm']) < 5:
            res['reason'].append(
                " Bank doesn't provide loan for less than 5 year")
        if int(res['income']) < loan_amount:
            if Total_Monthly_Debt_Payments:
                dti_ration = Total_Monthly_Debt_Payments / gross_monthly_income
                aaproved_loan_amount = res['income'] * dti_ration
                if aaproved_loan_amount < loan_amount:
                    res['reason'].append(
                        "Bank can approve only Rs" + str(aaproved_loan_amount))
            else:
                res['reason'].append(
                    " your Salary is not sufficient for getting Loan")
        if int(res['bankbalance']) < emi_value:
            res['reason'].append(
                " Your bank asset Value is less than the monthly EMI")
    return res['reason']
