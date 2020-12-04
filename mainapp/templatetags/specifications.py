from django import template

register = template.Library()  # necessary to custom decoration

TABLE_HEAD = """
                <table class="table">
                <tbody>
            """
TABLE_TAIL = """
                </tbody>
                </table>
            """
TABLE_CONTENT = """<tr>
                      <td>{name}</td>
                      <td>{value}</td>
                  </tr>
                  """

PRODUCT_SPEC = {
    'notebook': {
        'Diagonal': 'diagonal',
        'Display type': 'display_types',
        'Processor frequency': 'processor_freq',
        'RAM': 'ram',
        'Video card': 'video',
        'Time without charge': 'time_without_charge',
    },
    'smartphone': {
        'Diagonal': 'diagonal',
        'Display type': 'display_types',
        'resolution': 'resolution',
        'Battery volume': 'accum_volume',
        'Having a slot for SD': 'sd',
        'Main camera': 'main_camera_mp',
        'Frontal camera': 'frontal_camera_mp',
    },
    'power_bank': {
        'Voltage': 'voltage',
        'Ampere Flow': 'ampere_flow',
        'Fast charging': 'Fast_charging',
        'Wireless': 'wireless',
        'Capacity': 'capacity',
        'Size': 'size',
        'Weight': 'weight',
    }
}

def get_product_spec(product, model_name):
    table_content = ''
    for name, value in PRODUCT_SPEC[model_name].items():
        table_content += TABLE_CONTENT.format(name=name, value=getattr(product, value))
    return table_content


@register.filter  # use as filter in templates '|'
def product_spec(product):
    model_name = product.__class__._meta.model_name  # get the model name
    return TABLE_HEAD + get_product_spec(product, model_name) + TABLE_TAIL
