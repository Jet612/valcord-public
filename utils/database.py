import pymongo
from pymongo import MongoClient
import uuid
from typing import Union
from .convert import Converter
from valaw import objects
from datetime import datetime

from pymongo.results import UpdateResult

import os

MONGO_URI = os.getenv("MONGO_URI", "")
client = MongoClient(MONGO_URI)

admin_db = client["admin"]
valcord_db = client["valcordDB"]
stats_db = client["valorantStatsDB"]

### valcordDB Collections ###
guilds_collection = valcord_db["guilds"]
users_collection = valcord_db["users"]
valorant_info_collection = valcord_db["valorant_info"]
website_collection = valcord_db["website"]
votes_collection = valcord_db["votes"]

### valorantStatsDB Collections ###
matches_collection = stats_db["matches"]
matchlists_collection = stats_db["matchlists"]
valorant_users_collection = stats_db["users"]
valorant_match_custom_collection = stats_db["match_custom"]

converter = Converter()

class Guilds:
    def create_guild(
            self,
            guild_id: int,
            log_channel: int = None,
            autoroles: bool = False,
            rank_roles: dict = {},
            news: bool = False,
            news_channel: int = None,
            patch_notes: bool = False,
            patch_notes_channel: int = None
    ) -> pymongo.results.InsertOneResult:
        """Adds a new guild to the database"""
        guild = {
            "guild_id": guild_id,
            "log_channel": log_channel,
            "autoroles": autoroles,
            "rank_roles": rank_roles,
            "news": news,
            "news_channel": news_channel,
            "patch_notes": patch_notes,
            "patch_notes_channel": patch_notes_channel
        }
        return guilds_collection.insert_one(guild)
    
    def delete_guild(self, query: dict) -> pymongo.results.DeleteResult:
        """Deletes a guild from the GuildCollection."""
        return guilds_collection.delete_one(query)
    
    def get_guild(self, query: dict) -> Union[dict, None]:
        """Gets a guild from the GuildCollection."""
        return guilds_collection.find_one(query)
    
    def get_many_guilds(self, query: dict = {}) -> Union[list, None]:
        """Gets many guilds from the GuildCollection."""
        return list(guilds_collection.find(query))
    
    def update_guild(self, query: dict, update: dict, update_type: str = "$set") -> pymongo.results.UpdateResult:
        """Updates a guild in the GuildCollection."""
        return guilds_collection.update_one(query, {update_type: update})
    
    def update_many_guilds(self, query: dict, update: dict, update_type: str = "$set") -> pymongo.results.UpdateResult:
        """Updates many guilds in the GuildCollection."""
        return guilds_collection.update_many(query, {update_type: update})
    
class Users:
    def create_user(
            self,
            user_id: int,
            api_puuid: str = None,
            client_puuid: str = None,
            access_token: str = None,
            refresh_token: str = None,
            private: bool = False,
            rank: int = None,
            region: str = None,
    ) -> pymongo.results.InsertOneResult:
        """Adds a new user to the database"""
        user = {
            "user_id": user_id,
            "uuid": str(uuid.uuid4()),
            "api_puuid": api_puuid,
            "client_puuid": client_puuid,
            "access_token": access_token,
            "refresh_token": refresh_token,
            "private": private,
            "rank": rank,
            "region": region
        }
        return users_collection.insert_one(user)
    
    def delete_user(self, query: dict) -> pymongo.results.DeleteResult:
        """Deletes a user from the UserCollection."""
        return users_collection.delete_one(query)
    
    def get_user(self, query: dict) -> Union[dict, None]:
        """Gets a user from the UserCollection."""
        return users_collection.find_one(query)
    
    def get_many_users(self, query: dict = {}) -> Union[list, None]:
        """Gets many users from the UserCollection."""
        return list(users_collection.find(query))
    
    def update_user(self, query: dict, update: dict, update_type: str = "$set") -> pymongo.results.UpdateResult:
        """Updates a user in the UserCollection."""
        return users_collection.update_one(query, {update_type: update})
    
    def update_many_users(self, query: dict, update: dict, update_type: str = "$set") -> pymongo.results.UpdateResult:
        """Updates many users in the UserCollection."""
        return users_collection.update_many(query, {update_type: update})
    
class ValorantInfo:
    def create_new_info(self, name: str, data) -> pymongo.results.InsertOneResult:
        """Adds a new info to the database"""
        info = {
            "name": name,
            "data": data
        }
        valorant_info_collection.delete_many({"name": name}) # Only one info should exist at a time
        return valorant_info_collection.insert_one(info)
    
    def get_info(self, name: str) -> Union[dict, None]:
        """Gets a info from the ValorantInfoCollection."""
        return valorant_info_collection.find_one({"name": name})

class Website:
    def add_page_view(self, url: str) -> Union[pymongo.results.InsertOneResult, pymongo.results.UpdateResult]:
        """Adds a page view to the website database."""
        ### Check if page exists
        page_data = website_collection.find_one({"url": url})
        if page_data is None:
            website_collection.insert_one({"url": url, "views": 1})
        else:
            website_collection.update_one({"url": url}, {"$inc": {"views": 1}})
        total_page_data = website_collection.find_one({"url": "total"})
        if total_page_data is None:
            website_collection.insert_one({"url": "total", "views": 1})
        else:
            website_collection.update_one({"url": "total"}, {"$inc": {"views": 1}})

    def get_page_views(self, url: str) -> Union[dict, None]:
        """Gets the page views from the website database."""
        return website_collection.find_one({"url": url})
    
    def get_many_page_views(self, query: dict = {}) -> Union[list, None]:
        """Gets many page views from the website database."""
        return list(website_collection.find(query))
    
class Votes:
    def add_user(self, user_id: int, timestamp: int) -> pymongo.results.InsertOneResult:
        """Adds a vote to the votes database."""
        return votes_collection.insert_one({"user_id": user_id, "timestamp": timestamp, "remind": False, "votes": 0})
    
    def get_user(self, query: dict) -> Union[dict, None]:
        """Gets a user from the UserCollection."""
        return votes_collection.find_one(query)
    
    def get_many_users(self, query: dict = {}) -> Union[list, None]:
        """Gets many users from the UserCollection."""
        return list(votes_collection.find(query))
    
    def update_user(self, query: dict, update: dict, update_type: str = "$set") -> pymongo.results.UpdateResult:
        """Updates a user in the UserCollection."""
        return votes_collection.update_one(query, {update_type: update})
    
    def user_voted(self, user_id: int, timestamp: int) -> UpdateResult:
        """Called when a user votes."""
        return votes_collection.update_one({"user_id": user_id}, {"$set": {"timestamp": timestamp}, "$inc": {"votes": 1}})
    
class RiotAPICollection:
    def add_match(self, match: objects.MatchDto) -> pymongo.results.InsertOneResult:
        """Adds a match to the database"""
        if matches_collection.find_one({"matchInfo.matchId": match.matchInfo.matchId}) is None:
            return matches_collection.insert_one(converter.to_dict(match))
        
    def get_match(self, id: str) -> object | None:
        """Gets a match from the database"""
        data = matches_collection.find_one({"matchInfo.matchId": id})
        if data:
            return converter.to_object(data, objects.MatchDto)
        return None
    
    def add_matchlist(self, matchlist: objects.MatchlistDto) -> pymongo.results.InsertOneResult:
        """Adds a matchlist to the database"""
        # If the user doesn't already exists is the database add them and the matchlist
        # Else check for new matches and add them to the front of the matchlist
        if matchlists_collection.find_one({"puuid": matchlist.puuid}) is None:
            return matchlists_collection.insert_one(converter.to_dict(matchlist))
        else:
            old_matchlist = matchlists_collection.find_one({"puuid": matchlist.puuid})
            new_matchlist = converter.to_dict(matchlist)
            new_matches = []
            for match in new_matchlist["history"]:
                if match not in old_matchlist["history"]:
                    new_matches.append(match)
            new_history = new_matches + old_matchlist["history"]
            matchlists_collection.update_one({"puuid": matchlist.puuid}, {"$set": {"history": new_history}})
        
    def get_matchlist(self, puuid: str) -> objects.MatchlistDto | None:
        """Gets a matchlist from the database"""
        data = matchlists_collection.find_one({"puuid": puuid})
        if data:
            return converter.to_object(data, objects.MatchlistDto)
        return None

    def get_users_act_stats(self, puuid: str, season: str) -> dict | None:
        return valorant_users_collection.find_one({"puuid": puuid, "season": season})

    def update_user_stats(self, puuid: str, season: str, stats: dict) -> None:
        update_data = {
            "puuid": puuid,
            "season": season,
            "statistics": stats,
            "last_updated": int(datetime.utcnow().timestamp() * 1000)
        }
        valorant_users_collection.update_one(
            {"puuid": puuid, "season": season},
            {"$set": update_data},
            upsert=True
        )

    def update_custom_match(self, puuid: str, match_id: str, data: dict) -> None:
        update_data = {
            "puuid": puuid,
            "match_id": match_id,
            "data": data
        }
        valorant_match_custom_collection.update_one(
            {"puuid": puuid, "match_id": match_id},
            {"$set": update_data},
            upsert=True
        )

    def get_custom_match(self, puuid: str, match_id: str) -> dict | None:
        return valorant_match_custom_collection.find_one({"puuid": puuid, "match_id": match_id})