from utils.instagram_bot import InstagramBOT

bot = InstagramBOT()
bot.open_page()
bot.bypass_authorization('planlayici2022', 'planlayici2022&&')
bot.new_post(cover_filepath='/home/isa/jesus/projects/InstagramMediaBot/test.jpg', filepath='/home/isa/Downloads/test.mp4',text='videonun testi')
