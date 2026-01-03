import json

import requests
from django.conf import settings
import asyncio
from libsv1.utils.string import StringUtils


class AiService:
    @staticmethod
    def gpt_send_request(prompt, api_key=settings.OPENAI_API_KEY, model='gpt-4.1', timeout=900, result_as_text=False, proxy_url=None, debug=False):

        # openai.api_key = settings.OPENAI_API_KEY
        # response = openai.chat.completions.create(
        #     model="gpt-4o",
        #     messages=[{
        #         "role": "user",
        #         "content": prompt
        #     }],
        # )
        # content = response.choices[0].message.content

        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {api_key}',
        }
        payload = {
            # "model": "gpt-4o",
            # "model": "gpt-4.1-nano",
            # "model": "gpt-3.5-turbo",
            "model": model,
            "max_tokens": 32768,
            "temperature": 0.0,
            "top_p": 1.0,
            "messages": [
                {
                    "role": "system",
                    "content": "You are a helpful assistant that outputs only valid JSON."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "response_format": {
                "type": "json_object"
            },
        }

        # print(prompt)
        # exit()


        try:
            response = requests.request(
                method='POST',
                url="https://api.openai.com/v1/chat/completions",
                json=payload,
                headers=headers,
                timeout=timeout,
                proxies={"https": proxy_url} if proxy_url else {},
            )

            if debug:
                print(' ')
                print('GLOBAL ERROR', response)
                print('URL:', response.url)
                print('REASON:', response.reason)
                print('REQUEST BODY:', response.request.body)
                try:
                    print('RESPONSE JSON:', response.json())
                except:
                    print('RESPONSE TEXT:', response.text[:500])
                print(' ')
        except Exception as e:
            raise Exception(f'requests.request | Exception: {str(e)}') from e

        try:
            response.raise_for_status()
        except Exception as e:
            raise Exception(f'raise_for_status | Exception: {str(e)}') from e

        try:
            response = response.json()
        except Exception as e:
            raise Exception(f'response.json | Exception: {str(e)}') from e

        try:
            text = response['choices'][0]['message']['content']
        except Exception as e:
            raise Exception(f'message.content | Exception: {str(e)}') from e

        if result_as_text:
            return text

        try:
            return StringUtils.parse_json_from_string(text)
        except Exception as e:
            raise Exception(f'parse json | Exception: {str(e)}') from e

    @staticmethod
    async def async_gpt_send_request(prompt, api_key=None, model=None, timeout=None):
        return await asyncio.to_thread(AiService.gpt_send_request, prompt, api_key, model, timeout)

    @staticmethod
    def gpt_send_multi_request(prompt, api_key=None, model=None, timeout=None, count=2):
        async def async_tasks(prompt, api_key, model, timeout, count):
            tasks = []
            for i in range(count):
                tasks.append(AiService.async_gpt_send_request(prompt, api_key, model, timeout))
            return await asyncio.gather(*tasks)
        return asyncio.run(async_tasks(prompt, api_key, model, timeout, count))

    # ---------------------------------------------------------

    @staticmethod
    def gemini_send_request(prompt, api_key, model_url='https://generativelanguage.googleapis.com/v1beta/models', model_name='gemini-2.5-flash', timeout=100, proxy_url=None, tmp_proxy_url=None, debug=False):

        target_url = f"{model_url}/{model_name}:generateContent"

        headers = {
            'Content-Type': 'application/json',
            'x-goog-api-key': api_key,
        }
        payload = {
            "contents": [{
                "parts": [{"text": prompt}]
            }],
            "generationConfig": {
                "temperature": 0.2,
            }
        }

        try:
            if tmp_proxy_url:
                proxy_payload = {
                    'kdja3djd': 'd38dasd',
                    'url': target_url,
                    'post': json.dumps(payload),
                    'headers': json.dumps(headers),
                    'timeout': timeout
                }

                response = requests.post(
                    url=tmp_proxy_url,
                    data=proxy_payload,
                    timeout=timeout,
                    headers={'User-Agent': 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)',},
                )

            else:
                response = requests.post(
                    url=target_url,
                    json=payload,
                    headers=headers,
                    timeout=timeout,
                    proxies={"https": proxy_url} if proxy_url else {},
                )

            if debug:
                print(' ')
                print('GLOBAL ERROR', response)
                print('URL:', response.url)
                print('REASON:', response.reason)
                print('REQUEST BODY:', response.request.body)
                try:
                    print('RESPONSE JSON:', response.json())
                except:
                    print('RESPONSE TEXT:', response.text[:500])
                print(' ')

        except Exception as e:
            raise Exception(f'request execution | Exception: {str(e)}') from e

        try:
            response.raise_for_status()
        except Exception as e:
            raise Exception(f'raise_for_status | Exception: {str(e)}') from e

        try:
            response = response.json()
        except Exception as e:
            raise Exception(f'response.json | Exception: {str(e)}') from e

        if 'error' in response:
            error_details = response['error']
            raise Exception(f'response api | Error: {error_details.get('message')}')

        try:
            text = response['candidates'][0]['content']['parts'][0]['text']
        except Exception as e:
            raise Exception(f'response->text | Error: {str(e)}') from e

        return text
