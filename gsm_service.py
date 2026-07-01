import time, serial, warnings, re, os, requests, smtplib, json, urllib
from datetime import date
from email.mime.text import MIMEText
from yaml import full_load


def get_environment(env):
    """
    == Description ==
    Return the environment info
    == Arguments ==
    *${input_env}:* (string) (required) the input environment
    """
    try:
        return full_load(open('conf.yaml').read())[env]
    except FileNotFoundError:
        raise ValueError(f"Unable to find the configuration file in this environment: {env}")

def read_unread_sms(port, baud_rate, timeout, default_sleep_time, modem_sleep_time, sender_numbers):
    """
    == Description ==
    Connects to a GSM modem via serial port and reads unread SMS messages
    == Arguments ==
    *${port}:* (string) (required) the port name
    *${baud_rate}:* (int) (required) the baud rate value
    *${timeout}:* (int) (required) the timeout value
    *${default_sleep_time}:* (float) (required) the default sleep time value
    *${modem_sleep_time}:* (int) (required) the modem sleep time value
    *${sender_numbers}:* (string) (required) the list of sender phone number
    == Returns ==
    Return the index array
    """
    phone = serial.Serial(port = port, baudrate=int(baud_rate), timeout=int(timeout))
    index_arr = []
    try:
        time.sleep(1)
        phone.write(b'AT+CMGF=1\r')
        time.sleep(float(default_sleep_time))
        cmd = b'AT+CMGL="REC UNREAD"\r'
        phone.write(cmd)
        time.sleep(int(modem_sleep_time))
        response = phone.read_all().decode()
        temp = str(response) 
        print('response is {0}'.format(str(response)))
        today = date.today()
        two_digit_year = today.strftime('%y')
        two_digit_month = today.strftime("%m")
        two_digit_day = today.strftime('%d')
        senders = sender_numbers
        sender_arr = senders.split(',')
        for sender_phone_number in sender_arr:
            pattern = r"CMGL: \d+,\"REC UNREAD\",\"{0}\",\"\",\"{1}\/{2}\/{3}"\
                .format(sender_phone_number, two_digit_year, two_digit_month, two_digit_day)
            matches = re.findall(pattern, temp)
            for match in matches:
                matched_index = str(match)
                print('matched_index is {0}'.format(match))
                matched_index = matched_index.replace('CMGL: ', '').replace(',', '')\
                    .replace(str(sender_phone_number), '')\
                    .replace("\"{0}/{1}/{2}".format(two_digit_year, two_digit_month, two_digit_day), '')\
                    .replace('\"REC UNREAD\"', '').replace('\"','')
                print('my matched_index based on sender phone number is ' + matched_index)
                index_arr.append(matched_index)
    except serial.SerialException as e:
        warnings.warn('Error opening serial port: {0}', {e})
    except Exception as e:
        warnings.warn('An error occurred: {0}', {e})
    finally:
        phone.close()
    return index_arr

def read_message_based_on_index(port, baud_rate, timeout, default_sleep_time, modem_sleep_time, index=0, webhook_url=""):
    """
    == Description ==
    Connects to a GSM modem via serial port and reads unread SMS messages based on the specific index
    == Arguments ==
    *${port}:* (string) (required) the port name
    *${baud_rate}:* (int) (required) the baud rate value
    *${timeout}:* (int) (required) the timeout value
    *${default_sleep_time}:* (float) (required) the default sleep time value
    *${modem_sleep_time}:* (int) (required) the modem sleep time value
    *${index}:* (int) (required) the specific index
    *${webhook_url}:* (string) (required) the webhook url
    """
    phone = serial.Serial(port=port, baudrate=int(baud_rate), timeout=int(timeout))
    try:
        time.sleep(1)
        phone.write(b'AT+CMGF=1\r')
        time.sleep(float(default_sleep_time))      
        cmd = 'AT+CMGR={0}\r'.format(index).encode("utf-8")
        phone.write(cmd)
        time.sleep(int(modem_sleep_time))
        response = phone.read_all().decode()
        temp = str(response) 
        print('response is {0}'.format(str(response)))
        temp = temp.replace('AT+CMGF=1','').replace('OK', '').replace('AT+CMGR={0}'.format(index), '').strip()
        print('temp is {0}'.format(temp))
        status = send_teams_alert(message=str(temp), webhook_url=webhook_url)
        print('Sending Teams Alert status is {0}'.format(status))
    except serial.SerialException as e:
        warnings.warn('Error opening serial port: {0}', {e})
    except Exception as e:
        warnings.warn('An error occurred: {0}', {e})
    finally:
        phone.close()

def send_teams_alert(message, webhook_url):
    """
    == Description ==
    Send a message via Teams chat
    == Arguments ==
    *${message}:* (string) (required) the message content
    *${webhook_url}:* (string) (required) the webhook url
    == Returns ==
    The status code
    """
    payload = {
        "type": "message",
        "attachments": [
            {
                "contentType": "application/vnd.microsoft.card.adaptive",
                "content": {
                    "type": "AdaptiveCard",
                    "body": [{"type": "TextBlock", "text": message}],
                    "$schema": "http://adaptivecards.io",
                    "version": "1.0"
                }
            }
        ]
    }
    response = requests.post(
        webhook_url, 
        data=json.dumps(payload), 
        headers={'Content-Type': 'application/json'},
        verify=False 
    )
    return response.status_code

def main() -> None:
    """Main entry point of the script."""
    env = os.getenv("env", "sim1")
    port = get_environment(env)['port_name']
    baud_rate = get_environment(env)['baud_rate']
    timeout = get_environment(env)['timeout']
    default_sleep_time = get_environment(env)['default_sleep_time']
    modem_sleep_time = get_environment(env)['modem_sleep_time']
    sender_numbers = get_environment(env)['sender_numbers']
    webhook_url = get_environment(env)['webhook_url']
    index_arr = read_unread_sms(port, baud_rate, timeout, default_sleep_time, modem_sleep_time, sender_numbers)
    for index in index_arr:
        read_message_based_on_index(port, baud_rate, timeout, default_sleep_time, modem_sleep_time, index, webhook_url)

if __name__ == "__main__":
    main()