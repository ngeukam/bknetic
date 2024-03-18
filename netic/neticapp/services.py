def calculated_paid_amount(devise, budget):
    if(devise == 1 ):
        return budget * 0.05
    elif(devise == 2):
        return budget * 655 * 0.05
    else:
        return budget * 500 * 0.05

def remaining_amount(amount, paid_amount):
    return amount - paid_amount