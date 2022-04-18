def creditscore(totallend, totalborrow, lend , borrow):
    '''
        Generating Credit score for a user .
        Lend_dicr and borrow dict can be prepopulated in the memory so not to recreate it again and again
    '''
    totallend, totalborrow, lend , borrow = totallend['transaction_amount__sum'], totalborrow['transaction_amount__sum'], lend['transaction_amount__sum'], borrow['transaction_amount__sum']
    lend_dict = {}
    borrow_dict = {}
    lend_score = 0
    borrow_score = 0
    l = 1
    b = 100
    credit_borrow = 100
    credit_lend = 1100
    for i in range(10):
        for j in range(10):
            lend_dict[l] = credit_lend
            borrow_dict[b] = credit_borrow
            l += 1
            b -= 1
        credit_borrow += 100
        credit_lend += 100
    if lend:
        lend_score = lend_dict[int((lend/totallend) * 100)]
    if borrow:
        borrow_score = lend_dict[int((borrow/totalborrow) * 100)]
    return  lend_score + borrow_score
