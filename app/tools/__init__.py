import random


def get_random(n, total):
    box = [i for i in range(total)]
    out = []
    for i in range(n):
        index = random.randint(0, total - i - 1)
        out.append(box[index])
        box[index], box[total - i - 1] = box[total - i - 1], box[index]
    return out


def generate_form_input(item, scale='12'):
    if item.get('category', 'input') == 'input':
        input_type = item.get('type', 'text')
        if input_type == 'number':
            html = '<input type="number" min="' + item.get('min', '0') + '" name="' + item[
                'name'] + '" max="' + item.get('max', '100') + '" class="form-control">'
        else:
            html = '<input type="' + input_type + '" name="' + item['name'] + '" class="form-control">'
    else:  # select框
        html = '    <select name="' + item['name'] + '" class="form-control">'
        for option in item['options']:
            html += '  <option value="' + option['value'] + '">' + option['text'] + '</option>'

    return '<div class="col-sm-' + scale + '">' + \
           '  <div class="input-group" style="margin: 5px 0px;">' + \
           '    <span class="input-group-addon">' + item['text'] + '</span>' + \
           '      ' + html + \
           '    </select> ' + \
           '  </div>' + \
           '</div>'


def generate_form_html(form_array):
    form_input = ''

    for item in form_array:
        if type(item) == list:
            scale = str(12 // len(item))
            for i in item:
                form_input += generate_form_input(i, scale=scale)
        else:
            form_input += generate_form_input(item)

    form_html = '<div class="modal-body" style="display: flex;padding: 15px 0 0 0;">' + \
                '   <form>' + \
                '       ' + form_input + \
                '   </form>' + \
                '</div>'

    return form_html


if __name__ == "__main__":
    for i in get_random(10, 100):
        print(i, end=' ')
