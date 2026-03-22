from datetime import date
import time, serial, warnings, re

def read_unread_sms(port, baud_rate=115200, timeout=5):
    """
    Connects to a GSM modem via serial port and reads unread SMS messages.
    """
    phone = serial.Serial(port, baud_rate, timeout=timeout)

    try:
        # Set up serial connection (adjust port and baud_rate as necessary)
        # phone = serial.Serial(port, baud_rate, timeout=timeout)
        time.sleep(1)

        # Enable SMS text mode
        phone.write(b'AT+CMGF=1\r')
        time.sleep(0.5)
        
        # Command to list "REC UNREAD" messages
        cmd = b'AT+CMGL="REC UNREAD"\r'
        phone.write(cmd)
        time.sleep(3) # Give the modem time to respond

        # Read the response
        response = phone.read_all().decode()
        # warnings.warn('response is {0}', str(response))
        temp = str(response) 
        print('response is {0}'.format(str(response)))
        # start_point = 'UNREAD\"'
        # start_index = temp.index(start_point)
        # temp2 = temp[start_index + len(start_point):]
        # end_point = 'OK'
        # end_index = temp2.index(end_point)
        # temp3 = temp2[:end_index].strip()
        # print('temp2 is ' + temp2)
        # print('temp3 is ' + temp3)
        # pattern = r"CMGL: \d+,"
        today = date.today()
        two_digit_year = today.strftime('%y')
        two_digit_month = today.strftime("%m")
        two_digit_day = today.strftime('%d')
        senders = '38069,62823'
        sender_arr = senders.split(',')
        for sender_phone_number in sender_arr:
            pattern = r"CMGL: \d+,\"REC UNREAD\",\"{0}\",\"\",\"{1}\/{2}\/{3}"\
                .format(sender_phone_number, two_digit_year, two_digit_month, two_digit_day)
            matches = re.findall(pattern, temp)
            for match in matches:
                matched_string = str(match)
                print('matched_string is {0}'.format(match))
                matched_string = matched_string.replace('CMGL: ', '').replace(',', '')\
                    .replace(str(sender_phone_number), '')\
                    .replace("\"{0}/{1}/{2}".format(two_digit_year, two_digit_month, two_digit_day), '')\
                    .replace('\"REC UNREAD\"', '').replace('\"','')
                print('my matched_index based on sender phone number is ' + matched_string)
        # Close the connection
        # phone.close()



    except serial.SerialException as e:
        # print(f"Error opening serial port: {e}")
        warnings.warn('Error opening serial port: {0}', {e})
    except Exception as e:
        # print(f"An error occurred: {e}")
        warnings.warn('An error occurred: {0}', {e})

    finally:
        # This block always runs, ensuring the file is closed
        phone.close()

def read_sms_based_on_index(port, baud_rate=115200, timeout=5, index=0):
    """
    Connects to a GSM modem via serial port and reads unread SMS messages.
    """
    phone = serial.Serial(port, baud_rate, timeout=timeout)

    try:
        # Set up serial connection (adjust port and baud_rate as necessary)
        # phone = serial.Serial(port, baud_rate, timeout=timeout)
        time.sleep(1)

        # Enable SMS text mode
        phone.write(b'AT+CMGF=1\r')
        time.sleep(0.5)
        
        cmd = 'AT+CMGR={0}\r'.format(index).encode("utf-8")
        phone.write(cmd)
        time.sleep(3) # Give the modem time to respond

        # Read the response
        response = phone.read_all().decode()
        # warnings.warn('response is {0}', str(response))
        temp = str(response) 
        print('response is {0}'.format(str(response)))
        pattern = r"Your one-time code for use with your (Hyundai|Genesis) account is: \d{6}"
        match = re.search(pattern, temp)
        if match:
            matched_string = match.group()
            print('matched_string is {0}'.format(matched_string))
            pattern = r"\d{6}"
            otp_match = re.search(pattern, matched_string)
            if otp_match:
                otp = otp_match.group() 
                print('my otp is {0}'.format(otp))


    except serial.SerialException as e:
        # print(f"Error opening serial port: {e}")
        warnings.warn('Error opening serial port: {0}', {e})
    except Exception as e:
        # print(f"An error occurred: {e}")
        warnings.warn('An error occurred: {0}', {e})

    finally:
        # This block always runs, ensuring the file is closed
        phone.close()


# Example usage:
# On Linux, the port might be '/dev/ttyUSB0' or similar
# On Windows, the port might be 'COM3' or similar
# Replace '/dev/ttyUSB0' with your actual port name
# read_unread_sms('COM8')
read_sms_based_on_index('COM8', index=62)
# read_sms_based_on_index('COM8', index=65)