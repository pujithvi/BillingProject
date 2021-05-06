import cx_Oracle
import datetime
dsn = cx_Oracle.makedsn(host='localhost', port=1521, sid='orcl')
con = cx_Oracle.connect("cisadm", "cisadm", dsn)


class Bill:
    
    def __init__(self, bill_cyc_cd='', start_dt='', end_dt='', acct_id='', bill_dt='', rs_cd='', calc_amt=''):
        self.bill_id = self.createBill_ID()
        self.bill_cyc_cd = bill_cyc_cd
        self.start_dt = start_dt
        self.end_dt = end_dt
        self.acct_id = acct_id
        self.bill_dt = bill_dt
        self.due_dt = self.getDueDate(self.bill_dt, 45)
        self.rs_cd = rs_cd
        self.calc_amt = calc_amt
        self.descr_on_bill = 'A charge of ' + str(self.calc_amt) +  ' is produced for your gas consumption during service period starting ' + str(self.start_dt) + ' up to end date '  + str(self.end_dt)

    def createBill_ID(self):
        cur=con.cursor()
        sql_selectMostRecentBill = '''select bill_id from hs_ci_bill order by Bill_ID  desc'''
        cur.execute(sql_selectMostRecentBill)
        mostRecentBill_id = cur.fetchone()[0]
        bill_num = int(mostRecentBill_id.split('AS')[1].split('Y')[0]) + 1
        bill_id = 'SFGAS' + str(bill_num) + 'Y21'
        return bill_id

    def getDueDate(self, from_date, days_to_add):
        business_days_to_add = days_to_add
        current_date = from_date
        while business_days_to_add>0:
            current_date+=datetime.timedelta(days=1)
            weekday = current_date.weekday()
            if weekday>= 5:
                continue
            business_days_to_add-=1
        #return current_date+datetime.timedelta(days=45)
        return current_date

    