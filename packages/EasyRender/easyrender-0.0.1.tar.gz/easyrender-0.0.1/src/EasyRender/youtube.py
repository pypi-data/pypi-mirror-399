from EasyRender.custom_exception import InvalidURLException
from EasyRender.logger import logger
import re
from IPython.display import HTML, display

def render_youtube_video(url:str, width:int = 780, height:int = 315):
    try:

        regex = r"(?:youtube\.com.*(?:\?|&)v=|youtu\.be/|youtube\.com/(?:embed|shorts|live)/)([a-zA-Z0-9_-]{11})"
        match = re.search(regex,url)

        if not match:
            raise InvalidURLException(f"Invalid YouTube URL: {url}")
        
        video_id = match.group(1)

        embed_url = f"https://www.youtube-nocookie.com/embed/{video_id}"

        iframe = f"""
        <iframe width="{width}" height="{height}" 
        src="{embed_url}" 
        title="YouTube video player" 
        frameborder="0" 
        allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" 
        referrerpolicy="strict-origin-when-cross-origin" 
        allowfullscreen>
        </iframe>
        """

        display(HTML(iframe))
        logger.info('Youtube video rendered successfully.')

        return 'success'
        


    except Exception as e:
        raise e
