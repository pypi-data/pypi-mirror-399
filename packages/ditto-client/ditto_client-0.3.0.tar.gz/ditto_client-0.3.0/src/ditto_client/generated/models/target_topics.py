from enum import Enum

class Target_topics(str, Enum):
    __ThingsTwinEvents = "_/_/things/twin/events",
    __ThingsLiveCommands = "_/_/things/live/commands",
    __ThingsLiveEvents = "_/_/things/live/events",
    __ThingsLiveMessages = "_/_/things/live/messages",
    __PoliciesAnnouncements = "_/_/policies/announcements",
    __ConnectionsAnnouncements = "_/_/connections/announcements",

