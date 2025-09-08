from django.contrib import admin
from django.utils.html import format_html

from apps.models import Video


@admin.register(Video)
class VideoModelAdmin(admin.ModelAdmin):
    list_display = ['id', 'type', 'duration', 'quick_look']
    readonly_fields = ['duration']

    @admin.display(description='Video')
    def quick_look(self, obj):
        if obj and obj.file:
            modal_id = f"videoModal-{obj.pk or 'new'}"
            return format_html( # TODO deprecated
                """
                <a href="#" class="button" onclick="openVideoModal('{id}'); return false;">▶ Quick Look</a>

                <!-- Modal -->
                <div id="{id}" style="display:none;
                                      position:fixed;
                                      top:0; left:0; width:100%; height:100%;
                                      background:rgba(0,0,0,0.6);
                                      z-index:9999;
                                      justify-content:center;
                                      align-items:center;">
                    <div style="background:#111; padding:10px; border-radius:10px;">
                        <video width="640" height="360" controls>
                            <source src="{url}" type="video/mp4">
                            Your browser does not support the video tag.
                        </video>
                        <div style="text-align:center; margin-top:5px;">
                            <a href="#" class="button deletelink" onclick="closeVideoModal('{id}'); return false;">Close</a>
                        </div>
                    </div>
                </div>

                <script>
                function openVideoModal(id) {{
                    document.getElementById(id).style.display = "flex";
                }}
                function closeVideoModal(id) {{
                    var modal = document.getElementById(id);
                    var video = modal.querySelector("video");
                    video.pause();
                    modal.style.display = "none";
                }}
                </script>
                """,
                id=modal_id,
                url=obj.file.url,
            )
        return "No video"
