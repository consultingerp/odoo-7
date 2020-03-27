def migrate(cr, version):
    cr.execute('SELECT partner_id, vita_file, vita_file_filename, id_file, id_file_filename FROM ghu_student WHERE vita_file IS NOT NULL')
    students = cr.dictfetchall()
    if students:
        for student in students:
            cr.execute('UPDATE res_partner SET vita_file=%s, vita_file_filename=%s, id_file=%s, id_file_filename=%s WHERE id = %s', [student['vita_file'], student['vita_file_filename'], student['id_file'], student['id_file_filename'], student['partner_id']])