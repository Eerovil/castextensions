import re

from .util_androidviewclient import AndroidViewBase, loop_until


class Netflix(AndroidViewBase):
    def run(self, netflix_url):
        self.vc.device.shell("am force-stop com.netflix.mediaclient")
        self.vc.device.shell("am start -a android.intent.action.VIEW -d {}".format(netflix_url))

        def _cast(**kwargs):
            self.vc.dump(window="-1", sleep=1)
            self.vc.findViewById("com.netflix.mediaclient:id/ab_menu_cast_item").touch()
            self.vc.dump(window="-1", sleep=1)
            self.vc.findViewWithTextOrRaise(re.compile(self.chromecast_name)).touch()

        loop_until(_cast)

        def _play(**kwargs):
            self.vc.dump(window="-1", sleep=1)
            self.vc.findViewById("com.netflix.mediaclient:id/video_img").touch()

        loop_until(_play)
