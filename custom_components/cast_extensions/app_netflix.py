import re

from .util_androidviewclient import AndroidViewBase, loop_until


class Netflix(AndroidViewBase):
    def run(self, netflix_url):
        self.vc.device.shell("am force-stop com.netflix.mediaclient")
        self.vc.device.shell("am start -a android.intent.action.VIEW -d {}".format(netflix_url))

        def _cast(**kwargs):
            self.vc.dump(window="-1", sleep=1)
            self.vc.findViewById("com.netflix.mediaclient:id/ab_menu_cast_item").touch()
            self.vc.dump(window="-1", sleep=2)
            disconnect_btn = self.vc.findViewById("android:id/button1")
            if disconnect_btn:
                title = self.vc.findViewById("com.netflix.mediaclient:id/mdx_dialog_title")
                if title.text().strip() == self.chromecast_name:
                    # Already connected to correct chromecast
                    self.vc.device.shell("input keyevent KEYCODE_BACK")
                    return
                else:
                    disconnect_btn.touch()
                    self.vc.dump(window="-1", sleep=3)
            self.vc.findViewWithTextOrRaise(re.compile(self.chromecast_name)).touch()

        loop_until(_cast)

        def _play(**kwargs):
            self.vc.dump(window="-1", sleep=1)
            self.vc.findViewById("com.netflix.mediaclient:id/video_img").touch()

        loop_until(_play)
