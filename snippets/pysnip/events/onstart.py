from pyaloha.event import DictEvent, Event


# App launch event. It is not necessary visible for a user.
# Its properties are:
# connection: {None, wifi, mobile}
# in_roaming: {True, False}
# user_info.get_location(): None or (lat, lon)
# user_info.uid
# user_info.os: {0 (Unknown), 1 (Android), 2 (iOS)}

class TechnicalLaunch(DictEvent):
    keys = (
        '$launch',
    )

    __slots__ = tuple()

    @property
    def connection(self):
        if 'connected' not in self.data:
            return None
        return self.data.get('ctype', 'mobile')

    @property
    def in_roaming(self):
        if 'connected' not in self.data:
            return None
        return self.data.get('roaming', 'no') == 'yes'

    def __dumpdict__(self):
        d = super(TechnicalLaunch, self).__basic_dumpdict__()
        d.update({
            'connection': self.connection(),
            'in_roaming': self.in_roaming()
        })
        return d


# TechnicalLaunch event in iOS is always associated with a UI launch

class IOSVisibleLaunch(TechnicalLaunch):
    __slots__ = tuple()


# This event is trusted to be the one associated with an actual UI launch
# in Android

class AndroidVisibleLaunch(Event):
    keys = (
        '$onResume',
    )

    __slots__ = tuple()


# ALOHA:
# Sending when user update or install application.

# $iosDeviceInfo [
# browserUserAgent=Mozilla/5.0 (iPhone; CPU iPhone OS 10_3 like Mac OS X)
#   AppleWebKit/603.1.30 (KHTML, like Gecko)
#   Version/10.0 Mobile/14E269 Safari/602.1
# bundleIdentifier=com.mapswithme.full
# calendarIdentifier=gregorian
# deviceModel=iPhone
# deviceName=Dany iPhone
# deviceSystemName=iOS
# deviceSystemVersion=11.1.2
# deviceUserInterfaceIdiom=phone
# localeDecimalSeparator=.
# localeIdentifier=ko-Kore_KR
# localeMeasurementSystem=Metric
# preferredLanguages=ko-KR
# preferredLocalizations=ko
# screenBounds=0 0 320 568
# screenNativeBounds=0 0 750 1334
# screenNativeScale=2.343750
# screenScale=2.000000
# screens=1
# ]

# $androidDeviceInfo [
# accessibility_enabled=1
# airplane_mode_on=0
# auto_time=1
# auto_time_zone=1
# bluetooth_on=0
# build_brand=htc
# build_cpu_abi1=arm64-v8a
# build_cpu_abi2=armeabi-v7a
# build_cpu_abi3=armeabi
# build_device=htc_himaulatt
# build_display=MRA58K release-keys
# build_fingerprint=htc/himaulatt_htc_la_amx_spa/htc_himaulatt:6.0/MRA58K/726057.1:user/release-keys
# build_hardware=htc_hima
# build_host=ABM108
# build_id=MRA58K
# build_manufacturer=HTC
# build_model=HTC One M9
# build_product=himaulatt_htc_la_amx_spa
# build_serial=FA58LYJ01487
# build_tags=release-keys
# build_time=1.4574212E12
# build_type=user
# build_user=buildteam
# build_version_sdk=23
# data_roaming=0
# date_format=d/MM/yyyy
# display_density=3.0
# display_density_dpi=480
# display_height_pixels=1776
# display_scaled_density=3.0
# display_width_pixels=1080
# display_xdpi=442.451
# display_ydpi=443.345
# dpi=480
# font_scale=1.0
# install_non_market_apps=0
# locale_country=US
# locale_language=es
# locale_variant=
# mcc=716
# mnc=10
# mock_location=0
# screen_height_dp=567
# screen_off_timeout=120000
# screen_width_dp=360
# time_12_24=24
# ]


class DeviceInfo(DictEvent):
    keys = (
        '$androidDeviceInfo',
        '$iosDeviceInfo',
    )

    androidVersions = {
        '10': '2.3.3-2.3.7',
        '15': '4.0.3-4.0.4',
        '16': '4.1.x',
        '17': '4.2.x',
        '18': '4.3',
        '19': '4.4',
        '21': '5.0',
        '22': '5.1',
        '23': '6.0',
        '24': '7.0',
        '25': '7.1',
        '26': '8.0',
        '27': '8.1'
    }

    __slots__ = tuple()

    @property
    def lang(self):
        try:
            if self.key == '$androidDeviceInfo':
                return self.data['locale_language']
            elif self.key == '$iosDeviceInfo':
                return self.data['preferredLocalizations'][:2]
        except KeyError:
            pass

        return None

    @property
    def os_version(self):
        try:
            if self.key == '$androidDeviceInfo':
                return self.androidVersions[self.data['build_version_sdk']]
            elif self.key == '$iosDeviceInfo':
                return self.data['deviceSystemVersion']
        except KeyError:
            return None

    def __dumpdict__(self):
        return super(DeviceInfo, self).__basic_dumpdict__()
