import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command, ChatMemberUpdatedFilter
from config.config import TOKEN, MONGO_URI
from stats.main import generate_statistics
from db.db import add_message, update_user_message_count, add_new_user
import os
import asyncio
from aiogram import Router
from aiogram.types import FSInputFile, BufferedInputFile
from aiogram.enums import ChatMemberStatus

logging.basicConfig(level=logging.INFO)

bot = Bot(token=TOKEN)
dp = Dispatcher()
router = Router()

@router.message(Command("stats"))
async def send_stats(message: types.Message):
    try:
        logging.info("Generating statistics...")
        generate_statistics(MONGO_URI)
        if os.path.exists('/tmp/message_stats.png') and os.path.exists('/tmp/user_growth.png'):
            logging.info("Statistics generated successfully, sending files...")
            
            message_stats_photo = FSInputFile("/tmp/message_stats.png")
            result = await message.answer_photo(
                message_stats_photo,
                caption="Messages Statistics"
            )

            with open("/tmp/user_growth.png", "rb") as image_from_buffer:
                result = await message.answer_photo(
                    BufferedInputFile(
                        image_from_buffer.read(),
                        filename="User Growth Statistics.png"
                    ),
                    caption="User Growth Statistics"
                )
        else:
            logging.error("Statistics images not found.")
            await message.answer("Statistics generation failed. Images not found.")
    
    except Exception as e:
        logging.error(f"Error while generating or sending statistics: {e}")
        await message.answer("An error occurred while generating statistics.")


@router.chat_member(ChatMemberUpdatedFilter(member_status_changed=(ChatMemberStatus.LEFT, ChatMemberStatus.MEMBER)))
async def chat_member_handler(chat_member: types.ChatMemberUpdated):
    if chat_member.new_chat_member.status == 'member':
        user_id = chat_member.from_user.id
        
        await add_new_user(user_id)
        logging.info(f"New user {user_id} added to the group.")       


@router.message()
async def handle_message(message: types.Message):
    user_id = message.from_user.id
    message_id = message.message_id
    date = message.date
    await add_message(user_id, message_id, date)
    await update_user_message_count(user_id)
    logging.info(f"Message from user {user_id} added to database.")


async def main():
    dp.include_router(router)
    
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
