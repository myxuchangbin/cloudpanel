import requests

import datetime

class DoApi():
    def __init__(self, token):
        self.curl = requests.session()
        self.token = token
        self.user_data = ""
        self.api_url = 'https://api.digitalocean.com'
        self.curl.headers = {
            'Authorization': f'Bearer {token}',
            # 'Content-Type': 'application/json'
        }

    # 获取账号信息
    def get_account(self):
        try:
            url = f'{self.api_url}/v2/account'
            if not self.report_get(url):
                print('获取失败')
                return False
            self.account_info = self.result['account']
            return True
        except BaseException as e:
            print(e)
            return False

    # 获取余额
    def get_balance(self):
        try:
            url = f'{self.api_url}/v2/customers/my/balance'
            if not self.report_get(url):
                print('获取失败')
                return False
            print(self.result)
            self.balance_info = self.result
            return True
        except:
            return False

    # 获取实例列表
    def get_droplets(self, tag_name=''):
        url = f"{self.api_url}/v2/droplets?tag_name={tag_name}"
        if not self.report_get(url):
            print('获取失败')
            return False
        self.droplets = []
        # print(self.result['droplets'])
        for droplet in self.result['droplets']:
            # print(json.dumps(droplet))
            _data = {
                'droplet_id': droplet['id'],
                'name': droplet['name'],
                'memory': droplet['memory'],
                'vcpus': droplet['vcpus'],
                'disk': droplet['disk'],
                'status': droplet['status'],
                'create_time': datetime.datetime.strptime(droplet['created_at'], "%Y-%m-%dT%H:%M:%SZ") + datetime.timedelta(hours=8),
                'size_slug': droplet['size_slug'],
                'image_slug': droplet['image']['slug'],
                'region_slug': droplet['region']['slug'],
            }

            if droplet['image']['slug'] == None:
                _data['image_slug'] = ''

            for _ip in droplet['networks']['v4']:
                if _ip['type'] == 'public':
                    ip = _ip['ip_address']
                    break
                continue
            else:
                ip = ''
            _data.update({
                'ip': ip
            })
            self.droplets.append(_data)
            # self.delete_droplet(droplet['id'])
        return True

    # 创建实例
    def create_droplet(self, name='cloudpanel', password='admin7788==', count=1, region='sgp1', size='s-1vcpu-1gb', image='debian-12-x64'):
        try:
            url = f"{self.api_url}/v2/droplets"

            _data = {
                "names": [name] * int(count),
                # "name": name,
                # "user_data": USER_DATA.replace('admin7788==', password),
                "user_data": f"#!/bin/bash\n echo 'root:{password}' | chpasswd",
                "region": region,
                "size": size,
                "image": image,
                "ssh_keys": [],
                "ipv6": True,
                "tags": []
            }
            self.report_post(url, _data)
            print(self.result)
            if len(self.result['droplets']) >= 1: return '创建成功', True
            return '创建失败', False
        except BaseException as e:
            print(e)
            return f'创建失败: {e}', False

    # 获取密钥id
    def get_key_id(self):
        try:
            url = f"{self.api_url}/v2/account/keys"
            if not self.report_get(url):
                return False
            self.key_id = self.result['ssh_keys'][0]['id']
            return True
        except:
            return False

    def delete_droplet(self, droplet_id):
        try:
            url = f"{self.api_url}/v2/droplets/{droplet_id}"
            # print(url)
            ret = self.curl.delete(url, timeout=30)
            if ret.status_code == 204: return True
            return False
        except:
            return False

    @classmethod
    def get_images(cls):
        image_list = [
            'debian-12-x64',
            'debian-13-x64',
            'centos-stream-9-x64',
            'centos-stream-10-x64',
            'rockylinux-8-x64',
            'rockylinux-9-x64',
            'rockylinux-10-x64',
            'almalinux-8-x64',
            'almalinux-9-x64',
            'almalinux-10-x64',
            'ubuntu-22-04-x64',
            'ubuntu-24-04-x64',
            'ubuntu-25-04-x64',
            'ubuntu-25-10-x64'
        ]
        return image_list

    def get_regions(self):
        try:
            url = f"{self.api_url}/v2/regions"
            if not self.report_get(url):
                print('获取失败')
                return False
            _data = []
            for region in self.result['regions']:
                _region = {
                    'name': region['name'],
                    'slug': region['slug'],
                    'sizes': region['sizes'],
                }
                _data.append(_region)
            self.regions = _data
            return True
        except:
            return False

    @classmethod
    def get_region_map(cls):
        data_list = [
            ('nyc1', '美国-纽约1'),
            ('nyc2', '美国-纽约2'),
            ('nyc3', '美国-纽约3'),
            ('sfo1', '美国-旧金山1'),
            ('sfo2', '美国-旧金山2'),
            ('sfo3', '美国-旧金山3'),
            ('atl1', '美国-亚特兰大1'),
            ('ams2', '荷兰-阿姆斯特丹2'),
            ('ams3', '荷兰-阿姆斯特丹3'),
            ('sgp1', '亚太-新加坡1'),
            ('lon1', '英国-伦敦1'),
            ('fra1', '德国-法兰克福1'),
            ('tor1', '加拿大-多伦多1'),
            ('syd1', '澳大利亚-悉尼1'),
            ('blr1', '印度-班加罗尔1')
        ]
        return data_list

    @classmethod
    def get_region_dist(cls):
        region_dist = {
            'nyc1': '美国-纽约1',
            'nyc2': '美国-纽约2',
            'nyc3': '美国-纽约3',
            'sfo1': '美国-旧金山1',
            'sfo2': '美国-旧金山2',
            'sfo3': '美国-旧金山3',
            'atl1': '美国-亚特兰大1',
            'ams2': '荷兰-阿姆斯特丹2',
            'ams3': '荷兰-阿姆斯特丹3',
            'sgp1': '亚太-新加坡1',
            'lon1': '英国-伦敦1',
            'fra1': '德国-法兰克福1',
            'tor1': '加拿大-多伦多1',
            'blr1': '印度-班加罗尔1',
            'syd1': '澳大利亚-悉尼1'
        }
        return region_dist

    @classmethod
    def get_price_map(cls):
        data_list = [
            # Basic
            ('s-1vcpu-512mb-10gb', '1H/0.5G/10G/0.5T-$4'),
            ('s-1vcpu-1gb', '1H/1G/25G/1T-$6'),
            ('s-1vcpu-2gb', '1H/2G/50G/2T-$12'),
            ('s-2vcpu-2gb', '2H/2G/60G/3T-$18'),
            ('s-2vcpu-4gb', '2H/4G/80G/4T-$24'),
            ('s-4vcpu-8gb', '4H/8G/160G/5T-$48'),
            # INTEL
            ('s-1vcpu-1gb-intel', '1H/1G/25G/1T-$7-intel'),
            ('s-1vcpu-1gb-35gb-intel', '1H/1G/35G/1T-$8-intel'),
            ('s-1vcpu-2gb-intel', '1H/2G/50G/2T-$14-intel'),
            ('s-1vcpu-2gb-70gb-intel', '1H/2G/70G/2T-$16-intel'),
            ('s-2vcpu-2gb-intel', '2H/2G/60G/3T-$21-intel'),
            ('s-2vcpu-2gb-90gb-intel', '2H/2G/90G/3T-$24-intel'),
            ('s-2vcpu-4gb-intel', '2H/4G/80G/4T-$28-intel'),
            ('s-2vcpu-4gb-120gb-intel', '2H/4G/120G/4T-$32-intel'),
            ('s-4vcpu-8gb-intel', '4H/8G/160G/5T-$56-intel'),
            ('s-4vcpu-8gb-240gb-intel', '4H/8G/240G/5T-$64-intel'),
            ('s-4vcpu-16gb-320gb-intel', '4H/16G/320G/6T-$96-intel'),
            # AMD
            ('s-1vcpu-1gb-amd', '1H/1G/25G/1T-$7-amd'),
            ('s-1vcpu-2gb-amd', '1H/2G/50G/2T-$14-amd'),
            ('s-2vcpu-2gb-amd', '2H/2G/60G/3T-$21-amd'),
            ('s-2vcpu-4gb-amd', '2H/4G/80G/4T-$28-amd'),
            ('s-2vcpu-8gb-amd', '2H/8G/100G/5T-$42-amd'),
            ('s-4vcpu-8gb-amd', '4H/8G/160G/5T-$56-amd'),
            ('s-4vcpu-16gb-amd', '4H/16G/200G/6T-$84-amd'),
        ]
        return data_list

    # 统一get请求
    def report_get(self, url):
        try:
            ret = self.curl.get(url, headers=self.curl.headers)
            self.result = ret.json()
            return True
        except:
            return False

    # 统一get请求
    def report_post(self, url, data):
        try:
            ret = self.curl.post(url, data=data)
            self.result = ret.json()
            # print(ret.json())
            return True
        except BaseException as e:
            print(e)
            return False

    def test(self):
        url = f"{self.api_url}/v2/droplets?tag_name="
        ret = self.curl.get(url)
        print(ret.json())



if __name__ == '__main__':
    pass
