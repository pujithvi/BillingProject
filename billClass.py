class Bill:
    def __init__(self, bill_id='', bill_cyc_cd='', start_dt='', end_dt='', acct_id='', bill_dt='', due_dt='', rs_cd='', calc_amt='', descr_on_bill = ''):
        self.bill_id = bill_id
        self.bill_cyc_cd = bill_cyc_cd
        self.start_dt = start_dt
        self.end_dt = end_dt
        self.acct_id = acct_id
        self.bill_dt = bill_dt
        self.due_dt = due_dt
        self.rs_cd = rs_cd
        self.calc_amt = calc_amt
        self.descr_on_bill = descr_on_bill
