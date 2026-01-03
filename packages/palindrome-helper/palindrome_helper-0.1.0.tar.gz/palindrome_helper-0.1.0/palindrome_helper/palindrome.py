def is_palindrome(string):
    cleaned_str = str(string).lower().replace(" ", "")
    if cleaned_str == cleaned_str[::-1]:
        return True
    else:
        return False