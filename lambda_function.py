import os
import json
import logging

import slack
from dateutil.parser import parse
from datetime import timedelta

'''
token : OAuth access token for bot
channel : channel name in slack (including '#')
timeDifference : national standard time - GMT
'''

TOKEN = os.environ['token']
CHANNEL = os.environ['channel']
TIME_DIFFERENCE = os.environ['timeDifference']

logger = logging.getLogger()
logger.setLevel(logging.INFO)


# SNS에서 받은 ComparisonOperator 정보로부터 문장 생성
def check_comparison(oper):
    if oper == 'GreaterThanThreshold':
        return 'greater than the threshold'
    elif oper == 'GreaterThanOrEqualToThreshold':
        return 'greater than or equal to the threshold'
    elif oper == 'LessThanThreshold':
        return 'less than the threshold'
    else:
        return 'less than or equal to the threshold'


def lambda_handler(event, context):
    logger.info("Event: " + str(event))
    message = json.loads(event['Records'][0]['Sns']['Message'])     # json 형식으로 SNS 메시지 로드
    logger.info("Message: " + str(message))

    # 메시지에서 알람 이름, 알람 시각, 현재 상태, 트리거의 이름 등을 받아 저장
    alarm_name = message['AlarmName']
    alarm_time = message['StateChangeTime']
    new_state = message['NewStateValue']
    old_state = message['OldStateValue']
    trigger = message['Trigger']['MetricName']
    threshold = message['Trigger']['Threshold']

    # GMT 시각에 TIME_DIFFERENCE를 더해 해당 국가 시각으로 변경
    parsed_time = (parse(alarm_time) + timedelta(hours=int(TIME_DIFFERENCE))).strftime("%Y/%m/%d %H:%M:%S")

    # 메시지로부터 현재 데이터 값만 파싱해 저장
    comparison = check_comparison(message['Trigger']['ComparisonOperator'])

    # 최종 메시지 생성
    reason = None
    if new_state == 'INSUFFICIENT_DATA':
        reason = 'cannot find ' + trigger + ' data'
    else:
        data_point = ((message['NewStateReason'].split('['))[1].split())[0]
        if old_state == 'INSUFFICIENT_DATA':
            reason = 'now can find ' + trigger + ' data (value: ' + str(round(float(data_point), 1)) + ')'
        else:
            reason = trigger + '(' + str(round(float(data_point), 1)) + ')'\
                     + (' was ' if new_state == 'ALARM' else ' was not ')\
                     + comparison + '(' + str(threshold) + ')'
    client = slack.WebClient(TOKEN)

    # 메시지 디자인
    attachments = [
        {
            'color': 'good' if new_state == 'OK' else 'warning' if new_state == 'INSUFFICIENT_DATA' else 'danger',
            'pretext': '*```%s```*' % alarm_name,
            'text': '*State:* %s %s\n*Time:* %s\n\n*Reason* \n%s'
                    % (':white_check_mark:' if new_state == 'OK'
                       else ':warning' if new_state == 'INSUFFICIENT_DATA'
                       else ':question:', new_state, parsed_time, reason),
            'mrkdwn_in': ['text', 'pretext']
        }
    ]

    # 봇 이름, 아이콘 등을 설정하여 슬랙 채널에 메시지 전송
    client.chat_postMessage(channel=CHANNEL,
                            username='AWS Monitoring Bot',
                            icon_emoji=':robot_face:',
                            attachments=attachments)