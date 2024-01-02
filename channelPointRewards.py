from twitchio.ext import commands
import asyncio
import requests
import json
from pprint import pprint
class ChannelPointRewards():
    def __init__(self, bot: commands.Bot, config):
        self.bot = bot
        self.config = config
    
    async def create_reward(self, token, reward_name, reward_cost, reward_prompt, reward_input_required):
        await self.bot.user.create_custom_reward(
            token=self.bot.config['twitch_access_token'],
            title=reward_name,
            cost=reward_cost,
            prompt=reward_prompt,
            input_required=reward_input_required
        )
    
    async def get_rewards(self, token):
        return await self.bot.user.get_custom_rewards(
                token=self.bot.config['twitch_access_token'],
                only_manageable=True
            )
    
    async def enable_reward(self, token, reward_name, reward_cost, reward_prompt, reward_input_required, status):
        rewards = await self.get_rewards(token)
        count = 0
        for reward in rewards:
            if reward.title == reward_name:
                count += 1
                await self.update_reward(token, reward.id, reward_name, reward_cost, reward_prompt, reward_input_required, status)
                return
        if count == 0:
           await self.create_reward(token, reward_name, reward_cost, reward_prompt, reward_input_required)
    
    async def disable_reward(self, token, reward_name,  reward_cost, reward_prompt, reward_input_required, status):
        rewards = await self.get_rewards(token)
        update_tasks = [asyncio.create_task(self.update_reward(token, reward.id, reward_name, reward_cost, reward_prompt, reward_input_required, status)) for reward in rewards if reward.title == reward_name]
        await asyncio.wait(update_tasks, return_when=asyncio.ALL_COMPLETED)
    
    async def update_reward(self, token, reward_id, reward_name, reward_cost, reward_prompt, reward_input_required, status):
        print(f"Updating reward {reward_id} to {status}")
        url = f"https://api.twitch.tv/helix/channel_points/custom_rewards?broadcaster_id={self.bot.user_id}&id={reward_id}"
        headers = {
            'Client-ID': self.config['twitch_client_id'],
            'Authorization': f"Bearer {token}",
            'Content-Type': 'application/json'
        }
        data = {
            'is_enabled': f'{status}',
            'cost': f'{reward_cost}',
            'title': f'{reward_name}',
            'prompt': f'{reward_prompt}',
            'is_user_input_required': f'{reward_input_required}'
        }

        response = requests.patch(url, headers=headers, data=json.dumps(data))
        pprint(response.json())
        