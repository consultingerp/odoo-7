def migrate(cr, version):
    cr.execute('SELECT partner_id, skype FROM ghu_advisor WHERE skype IS NOT NULL')
    advisors = cr.dictfetchall()
    if advisors:
        for advisor in advisors:
            cr.execute('UPDATE res_partner SET skype=%s WHERE id = %s', [advisor['skype'], advisor['partner_id']])
    cr.execute('SELECT partner_id, skype FROM hr_employee WHERE skype IS NOT NULL')