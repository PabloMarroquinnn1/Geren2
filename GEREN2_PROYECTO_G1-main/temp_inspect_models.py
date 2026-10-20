env = env
for model_name in ['dms.file', 'dms.directory', 'mailing.mailing', 'ir.mail_server', 'crm.lead']:
    model = env[model_name]
    print('MODEL', model_name)
    for name, field in sorted(model._fields.items()):
        if name in {'name','directory_id','folder_id','attachment_id','content','datas','res_model','res_id','model','email_from','mailing_model_id','subject','body_html','state','smtp_host','smtp_port','smtp_user','smtp_pass','smtp_encryption','active'}:
            print(name, field.type, getattr(field, 'comodel_name', None), getattr(field, 'required', None))
    print('---')
env.cr.commit()
