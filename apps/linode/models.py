import json

from django.db import models
from libs.linode import LinodeApi

import datetime

# Create your models here.
class Account(models.Model):
    name = models.CharField('名称', max_length=200, default='', null=True, blank=True)
    euuid = models.CharField('uuid', max_length=50, blank=True)
    email = models.EmailField('Email', default='', blank=True)
    password = models.CharField('密码', max_length=255, default='', blank=True)
    token = models.CharField('Token', max_length=100, db_index=True, unique=True)

    status = models.BooleanField('状态', max_length=25, default=True, blank=True)

    balance = models.CharField('余额', max_length=25, default='', blank=True)

    active_promotions = models.TextField('优惠详情', blank=True, default='')

    note = models.CharField('备注信息', max_length=50, default='', blank=True)

    create_time = models.DateTimeField('创建时间', null=True, auto_now_add=True)
    update_time = models.DateTimeField('更新时间', null=True, auto_now=True)

    def __str__(self):
        return self.token

    class Meta:
        verbose_name = "账户管理"
        verbose_name_plural = verbose_name

    # 获取账户信息
    def get_account(self):
        try:
            linode = LinodeApi(token=self.token)
            if not linode.get_account():
                self.status = False
                self.save()
                return '更新账号失败', False

            self.status = True
            self.email = linode.result.get('email', '')
            self.balance = linode.result['balance']
            active_promotions = linode.result['active_promotions']
            self.active_promotions = json.dumps(active_promotions)
            self.save()
            return '更新完成', True
        except BaseException as  e:
            return f'更新失败 {e}', False

    def update_instances(self):
        try:
            now_time = datetime.datetime.now()
            linode = LinodeApi(self.token)
            if not linode.get_instances():
                return '更新账号失败', False

            for foo in linode.instances:
                foo.update({
                    'account_id': self.id,
                    'update_time': datetime.datetime.now()
                })
                instance_id = foo['instance_id']
                if Vm.objects.filter(instance_id=instance_id):
                    Vm.objects.filter(instance_id=instance_id).update(**foo)
                    continue
                Vm.objects.create(**foo)
                continue
            Vm.objects.filter(update_time__lt=now_time, account_id=self.id).delete()
            return True
        except:
            return False

    # 获取虚拟机数量
    def get_vm_count(self):
        return Vm.objects.filter(account_id=self.id).count()

    # 创建vm
    def create_vm(self, region, vm_size, image_id, password, name=''):
        linode = LinodeApi(self.token)
        if not linode.create_instance(region, vm_size, image_id, password, name):
            return '创建失败', False

        # print(linode.result)
        if linode.result.get('errors'):
            return linode.result.get('errors'), False

        instance = linode.result
        try:
            ipv4 = instance['ipv4'][0]
        except:
            ipv4 = ''
        _instance = {
            'account_id': self.id,
            'instance_id': instance['id'],
            'label': instance['label'],
            'status': instance['status'],
            'password': password,
            'create_time': instance['created'],
            'type': instance['type'],
            'ipv4': ipv4,
            'ipv6': instance['ipv6'],
            'image': instance['image'],
            'region': instance['region']
        }
        Vm.objects.create(**_instance)
        return '创建成功', True

    def get_active_promotions(self):
        try:
            return json.loads(self.active_promotions)[0]
        except:
            return {}

class Vm(models.Model):
    account = models.ForeignKey('Account', on_delete=models.CASCADE, verbose_name='所属账号',
                                related_name='ld_account')
    instance_id = models.IntegerField('实例ID')
    label = models.CharField('名称', max_length=100, default='', blank=True)
    status_choices = (
        ('shutting_down', '关机中'),
        ('provisioning', '创建中'),
        ('rebuilding', '重装中'),
        ('rebooting', '重启中'),
        ('deleting', '删除中'),
        ('running', '运行中'),
        ('booting', '启动中'),
        ('stopped', '已关机'),
    )

    status = models.CharField('名称', max_length=20, choices=status_choices, blank=True)

    type_choices = (
        ("g6-nanode-1", "1vCPU, 1GB, 25GB, 1T, $5"),
        ("g6-standard-1", "1vCPU, 2GB, 50GB, 2T, $12"),
        ("g6-standard-2", "2vCPU, 4GB, 80GB, 4T, $24"),
        ("g6-standard-4", "4vCPU, 8GB, 160GB, 5T, $48"),
        ("g6-standard-6", "6vCPU, 16GB, 320GB, 6T, $96"),
        ("g7-highmem-1", "2vCPU, 24GB, 20GB, 5T, $60"),
        ("g6-dedicated-2", "2vCPU, 4GB, 80GB, 4T, $36"),
        ("g6-dedicated-4", "4vCPU, 8GB, 160GB, 5T, $72"),
        ("g7-premium-2", "2vCPU, 4GB, 80GB, 4T, $43"),
        ("g7-premium-4", "4vCPU, 8GB, 160GB, 5T, $86")
    )
    type = models.CharField('实例规格', max_length=20, choices=type_choices, blank=True)

    images_choices = (
        ('linode/almalinux8', 'AlmaLinux 8'),
        ('linode/almalinux9', 'AlmaLinux 9'),
        ('linode/almalinux10', 'AlmaLinux 10'),
        ('linode/alpine3.19', 'Alpine 3.19'),
        ('linode/alpine3.20', 'Alpine 3.20'),
        ('linode/alpine3.20', 'Alpine 3.21'),
        ('linode/alpine3.20', 'Alpine 3.22'),
        ('linode/arch', 'Arch Linux'),
        ('linode/centos-stream9', 'CentOS Stream 9'),
        ('linode/centos-stream10', 'CentOS Stream 10'),
        ('linode/debian11', 'Debian 11'),
        ('linode/debian12', 'Debian 12'),
        ('linode/debian13', 'Debian 13'),
        ('linode/fedora41', 'Fedora 41'),
        ('linode/fedora42', 'Fedora 42'),
        ('linode/fedora43', 'Fedora 43'),
        ('linode/gentoo', 'Gentoo'),
        ('linode/kali', 'Kali Linux'),
        ('linode/opensuse15.6', 'openSUSE Leap 15.6'),
        ('linode/rocky8', 'Rocky Linux 8'),
        ('linode/rocky9', 'Rocky Linux 9'),
        ('linode/rocky10', 'Rocky Linux 10'),
        ('linode/slackware15.0', 'Slackware 15.0'),
        ('linode/ubuntu20.04', 'Ubuntu 20.04 LTS'),
        ('linode/ubuntu22.04', 'Ubuntu 22.04 LTS'),
        ('linode/ubuntu24.04', 'Ubuntu 24.04 LTS'),
        ('linode/ubuntu25.10', 'Ubuntu 25.10'),
    )

    image = models.CharField('镜像地址', max_length=50, choices=images_choices, blank=True)

    regions_choices = (
        ('jp-osa', '日本-大阪'),
        ('ap-northeast', '日本-东京2'),
        ('jp-tyo-3', '日本-东京3'),
        ('ap-south', '新加坡'),
        ('sg-sin-2', '新加坡2'),
        ('ap-west', '印度'),
        ('in-bom-2', '印度-孟买2'),
        ('in-maa', '印度-清奈'),
        ('eu-central', '德国'),
        ('de-fra-2', '德国-法兰克福2'),
        ('ca-central', '加拿大'),
        ('ap-southeast', '澳大利亚'),
        ('au-mel', '澳大利亚-墨尔本'),
        ('eu-west', '英国-伦敦'),
        ('gb-lon', '英国-伦敦2'),
        ('us-central', '美国中部-达拉斯'),
        ('us-west', '美国西部-费利蒙'),
        ('us-southeast', '美国南部-亚特兰大'),
        ('us-east', '美国东部-新泽西'),
        ('us-iad', '美国-华盛顿'),
        ('us-mia', '美国-迈阿密'),
        ('us-ord', '美国-芝加哥'),
        ('us-sea', '美国-西雅图'),
        ('us-lax', '美国-洛杉矶'),
        ('fr-par', '法国-巴黎'),
        ('es-mad', '西班牙-马德里'),
        ('br-gru', '巴西-圣保罗'),
        ('nl-ams', '荷兰-阿姆斯特丹'),
        ('se-sto', '瑞典-斯德哥尔摩'),
        ('it-mil', '意大利-米兰'),
        ('id-cgk', '印尼-雅加达'),
    )

    region = models.CharField('镜像地址', max_length=20, choices=regions_choices, blank=True)

    ipv4 = models.GenericIPAddressField('IPV4', blank=True, null=True, default='')
    ipv6 = models.GenericIPAddressField('IPV6', blank=True, null=True, default='')

    password = models.CharField('密码', max_length=200, default='', blank=True)

    create_time = models.DateTimeField('创建时间', null=True, auto_now_add=True)
    update_time = models.DateTimeField('更新时间', null=True, auto_now=True)

    def __str__(self):
        return self.instance_id

    class Meta:
        verbose_name = "实例管理"
        verbose_name_plural = verbose_name

    def get_type(self):
        return ', '.join(self.get_type_display().split(',')[:2])

    def vm_power_action(self, action):
        linodeApi = LinodeApi(self.account.token)
        if not linodeApi.power_action(self.instance_id, action):
            return False
        self.account.update_instances()
        return True

    def delete_linode(self):
        linodeApi = LinodeApi(self.account.token)
        if not linodeApi.delete_instance(self.instance_id):
            return False
        self.account.update_instances()
        return True
