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


def emiResponse(res,loan_term,cibil,loan_amount):
    if cibil>750:
        P=loan_amount
        res["reason"]=[]
        res["reason"].append("Interest rate is 15.5%")
        res["interest_rate"]=15.5
        r=15.5
        res["reason"].append("Your Loan Amount is "+str(loan_amount))
        res["loan_amount"]=loan_amount
        res["reason"].append("Your Loan term is "+ str(loan_term) + " years")
        loan_term=loan_term*12
        res["emi"]=(P * (r / 1200)) / (1 - (1 + (r / 1200)) ** (-loan_term))
        res["reason"].append("Your EMI amount is "+ str(round(res["emi"])))

    else:
        P=loan_amount
        res["reason"]=[]
        res["reason"].append("Interest rate is 27.5%")
        r=27.5
        res["interest_rate"]=r
        res["reason"].append("Your Loan Amount is "+str(loan_amount))
        res["loan_amount"]=loan_amount
        res["reason"].append("Your Loan term is "+ str(loan_term) + " years")
        loan_term=loan_term*12
        res["emi"]=(P * (r / 1200)) / (1 - (1 + (r / 1200)) ** (-loan_term))
        res["reason"].append("Your EMI Amount is "+ str(round(res["emi"])))
    return res
        
    
    