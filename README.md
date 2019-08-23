# CloudwatchToPrettySlack

## 정보

aws Cloudwatch에서 경보가 발생할 때 Slack에 알리는 람다 함수입니다.

## 사용법

> ### Cloudwatch 지표 생성

1. [aws 홈페이지](https://aws.amazon.com/) > Cloudwatch > 경보 > `경보 생성` 클릭

2. 지표 선택 후 경보를 울릴 범위 설정

    > ![condition](src/condition.png)

3. 기준에 도달했을 때 울릴 경보(SNS) 이름 설정 > `주제 생성` 클릭

    > ![set_alarm](src/set_alarm.png)
    
4. 정상 상태로 돌아왔을 때 경보 설정

    - `알림 추가` 클릭 > 정상 상태를 알릴 SNS 선택
    
    > ![set_ok](src/set_ok.png)
    
5. 경보 이름 설정 후 `경보 생성` 클릭

> ### zip 파일 얻기


1. Python virtualenv 설치

```
# terminal

pip3 install virtualenv
```

2. 해당 레포지토리 clone

3. clone한 디렉토리 안으로 이동하여 venv 설정

```
# cloned_directory

virtualenv venv
```

4. venv 활성화

```
# cloned_directory

source venv/bin/activate
```

5. venv 안에 함수 실행을 위한 모듈들 설치

```
# (venv) cloned_directory

pip3 install slack slackclient datetime python-dateutil
```

6. venv 비활성화
```
# (venv) cloned_directory

deactivate
```

7. 다음 명령어를 실행하여 디렉토리에 zip 파일 생성

```
# cloned_directory

cd venv/lib/python3.7/site-packages/
zip -r ../../../../cloudWatchToPrettySlack.zip ./*
cd ../../../../
zip -ur cloudWatchToPrettySlack.zip lambda_function.py
```
    
> Lambda 함수 생성

1. aws 홈페이지 > Lambda > 함수 > `함수 생성` 클릭

2. 런타임 : Python 3.7 설정

3. 생성했던 SNS 경보를 트리거 목록에 추가

4. 함수 코드 설정 > `.zip파일 업로드` 선택 후 zip파일 업로드

    * 핸들러 : `lambda_function.lambda_handler` 입력

    > ![set_lambda](src/set_lambda.png)
    
5. 환경 변수 설정

    - **token**

        - Bot user OAuth access token (ex. `xoxb-tokentoken-yourtoken`)
        
            > [Slack API](https://api.slack.com) > Create New App > Bot User 메뉴에서 봇 생성
            >
            > OAuth & Permission 메뉴에서 Bot user 토큰 복사
            >
            > ![OAuth_token](src/OAuth_token.png)
            >
            > 해당 토큰이 없다면 `Reinstall App` 버튼을 통해 생성가능
            
    - **channel**
    
        - 메시지를 발송할 Slack 채널 이름, '#'을 포함해서 적어야 함 (ex. `#your_channel`)
    
    - **timeDifference**
    
        - 국가 표준시와 GMT 표준시의 차 (ex. 한국: `9`, 영국: `1`)
        
    입력 완료 예시
    
    ![environment_variables](src/environment_variables.png)
    
## 실행 결과

> State - Alarm
>
>![Alarm](./src/state_alarm.png)

> State - OK
>
>![OK](./src/state_ok.png)

## 참고

Cloudwatch SNS Alarm 예시

```
{
    "AlarmName": "CPU Alarm",
    "AlarmDescription": "Created from EC2 Console",
    "AWSAccountId": "1234567890",
    "NewStateValue": "ALARM",
    "NewStateReason": "Threshold Crossed: 1 out of the last 1 datapoints [12.800296378623722 (26/06/19 03:44:00)] was greater than or equal to the threshold (10.0) (minimum 1 datapoint for OK -> ALARM transition).",
    "StateChangeTime": "2019-06-26T03:54:21.746+0000",
    "Region": "Asia Pacific (Seoul)",
    "OldStateValue": "OK",
    "Trigger":
    {
        "MetricName": "CPUUtilization",
        "Namespace": "AWS/EC2",
        "StatisticType": "Statistic",
        "Statistic": "AVERAGE",
        "Unit": null,
        "Dimensions":
        [
            {
                "value": "i-abc1234567890",
                "name": "InstanceId"
            }
        ],
        "Period": 300,
        "EvaluationPeriods": 1,
        "ComparisonOperator": "GreaterThanOrEqualToThreshold",
        "Threshold": 10.0,
        "TreatMissingData": "",
        "EvaluateLowSampleCountPercentile": ""
    }
}
```