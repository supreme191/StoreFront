from django.core.exceptions import ValidationError

def valid_file_size(file) :
    max_size = 500

    if file.size > max_size * 1024 :
        raise ValidationError(f'Files cannot be larger that {max_size}KB!')