import cx_Oracle
import datetime
dsn = cx_Oracle.makedsn(host='localhost', port=1521, sid='orcl')
con = cx_Oracle.connect("cisadm", "cisadm", dsn)


class Bill:
    
    def __init__(self, bill_cyc_cd=None, start_dt=None, end_dt=None, acct_id=None, agl_charge = None, gas_usage = None, 
                 bill_dt=None, rs_cd=None, calc_amt=None, exp_msg ='No errors have been found'):
        if calc_amt != None:
            self.bill_id = self.createBill_ID()
        else:
            self.bill_id=None
        self.bill_cyc_cd = bill_cyc_cd
        if start_dt != None:
            self.start_dt = datetime.date(start_dt.year, start_dt.month, start_dt.day)
        else:
            self.start_dt = None
        if end_dt != None:
            self.end_dt = datetime.date(end_dt.year, end_dt.month, end_dt.day)
        else:
            self.end_dt=None
        self.acct_id = acct_id
        if bill_dt != None:
            self.bill_dt = datetime.date(bill_dt.year, bill_dt.month, bill_dt.day)
        else:
            self.bill_dt = None
        self.agl_charge=agl_charge
        self.gas_usage = gas_usage
        if bill_dt != None:
            self.due_dt = self.getDueDate(self.bill_dt, 45)
            self.due_dt = datetime.date(self.due_dt.year, self.due_dt.month, self.due_dt.day)
        else:
            self.due_dt = None
        self.rs_cd = rs_cd
        self.calc_amt = calc_amt
        if self.calc_amt != None and self.start_dt!= None and self.end_dt!=None:
            self.descr_on_bill = 'A charge of ' + str(self.calc_amt) +  ' is produced for your gas consumption during service period starting ' + 
            str(self.start_dt) + ' up to end date '  + str(self.end_dt)
        self.exp_msg = exp_msg

    def createBill_ID(self):
        cur=con.cursor()
        sql_selectMostRecentBill = '''select bill_id from hs_ci_bill order by Bill_ID  desc'''
        cur.execute(sql_selectMostRecentBill)
        mostRecentBill_id = cur.fetchone()[0]
        bill_num = int(mostRecentBill_id.split('AS')[1].split('Y')[0]) + 1
        bill_id = 'SFGAS' + str(bill_num) + 'Y21'
        return bill_id

    def getDueDate(self, from_date, days_to_add):
        if from_date == None:
            return None

        business_days_to_add = days_to_add
        current_date = from_date
        while business_days_to_add>0:
            current_date+=datetime.timedelta(days=1)
            weekday = current_date.weekday()
            if weekday>= 5:
                continue
            business_days_to_add-=1
        return current_date

    
