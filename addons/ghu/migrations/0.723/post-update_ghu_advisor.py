def migrate(cr, version):
    cr.execute('SELECT partner_id, vita, vita_filename FROM ghu_advisor WHERE vita IS NOT NULL')
    advisors = cr.dictfetchall()
    if advisors:
        for advisor in advisors:
            cr.execute('UPDATE res_partner SET vita_file=%s, vita_file_filename=%s WHERE id = %s', [advisor['vita'], advisor['vita_filename'], advisor['partner_id']])