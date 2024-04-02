def send_otp_code(phone_number, otpcode):
    try:
       print('inside funtion to send otp code')
    except BaseException as e:
        return ({'message': str(e)})
    return