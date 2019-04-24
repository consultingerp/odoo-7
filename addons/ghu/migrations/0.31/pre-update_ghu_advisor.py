def migrate(cr, version):
    cr.execute('SELECT partner_id, last_name FROM ghu_advisor WHERE last_name IS NOT NULL')
    advisors = cr.dictfetchall()
    if advisors:
        for advisor in advisors:
            cr.execute('UPDATE res_partner SET lastname=%s WHERE id = %s', [advisor['last_name'], advisor['partner_id']])