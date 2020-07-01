class BootStrapForm(object):
    # 哪些标签不应用样式
    bootstrap_class_exclude = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if name in self.bootstrap_class_exclude:
                continue
            field.widget.attrs['class'] = 'form-control'
            field.widget.attrs['placeholder'] = '请输入%s' % (field.label,)