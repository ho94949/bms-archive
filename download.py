import os
import requests


def Download(url, path, total_length=70):

    bar_length = total_length - 8
    with open(path, 'wb') as f:
        print('Downloading ' + os.path.basename(path))

        r = requests.get(url, stream=True)
        total_length = r.headers.get('Content-Length')

        # total_length can be None
        try:
            total_length = int(total_length)
        except ValueError:
            total_length = None
            pass
        except TypeError:
            total_length = None
            pass

        download_bytes = 0

        for data in r.iter_content(chunk_size=4096):
            download_bytes += len(data)
            f.write(data)

            if not((total_length is None) or (total_length == 0)):
                ratio = download_bytes / total_length
                per = int(ratio * 100)
                barl = max(1, int(ratio * bar_length))
                bar = '=' * (barl - 1) + '>' + ' ' * (bar_length - barl)
            else:
                per = '???'
                bar = '?' * bar_length

            print('{0:4}% [{1}]'.format(per, bar), end='\r')

    print('{0:4}% [{1}]'.format(100, '=' * bar_length))
