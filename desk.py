from __future__ import division
import json
import copy

DOWN = -1
UP = 1
STATIC = 0
HTP = 0
LTP = 1

FPS = 10


class Channel(object):
    """ A representation of a single channel and its current value """
    def __init__(self, channel_number, channel_value):
        self.channel_number = channel_number
        self.channel_value = channel_value

    def __repr__(self):
        return ('Channel(channel_number=%s, channel_value=%s)'
                % (repr(self.channel_number), repr(self.channel_value)))


class ChannelTarget(Channel):
    """ An extension of Channel that adds control for stepping it in the correct direction to its target """
    def __init__(self, channel_number, target_value):
        super(ChannelTarget, self).__init__(channel_number, 0)
        self.target_value = target_value
        self.step_amount = 0

    def __repr__(self):
        return ('ChannelTarget(channel_number=%s, channel_value=%s, target_value=%s, step_amount=%s)'
                % (repr(self.channel_number), repr(self.channel_value), repr(self.target_value), repr(self.step_amount)))

    def direction(self):
        """ Return channel direction to target value """
        if self.channel_value - self.target_value < 0:
            return UP
        elif self.channel_value - self.target_value > 0:
            return DOWN
        else:
            return STATIC

    def step(self):
        """ Move channel value one increment closer to target """
        if self.direction() == UP:
            self.channel_value = self.channel_value + self.step_amount
            if self.channel_value > self.target_value:
                self.channel_value = self.target_value

        if self.direction() == DOWN:
            self.channel_value = self.channel_value - self.step_amount
            if self.channel_value < self.target_value:
                self.channel_value = self.target_value

    def set_running(self, current_channels, fade_time):
        """ Set current value of all channels and set step_amount """
        for channel in current_channels:
            if channel.channel_number == self.channel_number:
                self.channel_value = channel.channel_value
                if self.direction() == UP:
                    self.step_amount = (self.target_value - self.channel_value) / (FPS * fade_time)
                elif self.direction() == DOWN:
                    self.step_amount = (self.channel_value - self.target_value) / (FPS * fade_time)
                break

    def to_json(self):
        """ Output ChannelTarget as a json string """
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True)


class Cue(object):
    """ A cue holds channel info at their desired target values as well as fade time """
    def __init__(self, cue_number, fade_time):
        self.cue_number = cue_number
        self.fade_time = fade_time
        self.channels = []

    def __repr__(self):
        return_string = ('Cue(cue_number=%s, fade_time=%s)'
                         % (repr(self.cue_number), repr(self.fade_time)))

        for channel in self.channels:
            return_string = return_string + '\n\t' + str(channel)

        return return_string

    def add_channel(self, channel_number, target_value):
        """ Add channel to cue unless exists, then update """
        found = False
        for channel in self.channels:
            if channel.channel_number == channel_number:
                found = True
        if found is True:
            self.modify_channel(channel_number, target_value)
        else:
            self.channels.append(Channel(channel_number, target_value))

    def remove_channel(self, channel_number):
        """ Remove channel from cue """
        new_channels = []
        for channel in self.channels:
            if channel.channel_number != channel_number:
                new_channels.append(channel)
        self.channels = new_channels

    def modify_channel(self, channel_number, target_value):
        """ Modify channel if exists """
        for channel in self.channels:
            if channel.channel_number == channel_number:
                channel.target_value = target_value

    def to_json(self):
        """ Return Cue as a json string """
        return_string = "{\"cue_number\": " + str(self.cue_number) + ", \"channels\": "
        return_string = return_string + "["
        for channel in self.channels:
            return_string = return_string + channel.to_json()
            return_string = return_string + ","
        return_string = return_string[:-1] + "], \"fade_time\": " + str(self.fade_time) + "}"

        return return_string

    def from_json(self, json_string):
        """ Return new Cue object from json string """
        loaded_cue = json.loads(json_string)
        cue_copy = Cue(loaded_cue["cue_number"], loaded_cue["fade_time"])
        for channel in loaded_cue["channels"]:
            cue_copy.add_channel(channel["channel_number"], channel["target_value"])
        return cue_copy


class CueRunning(Cue):
    """ CueRunning is an extension of Cue allowing all channels to be moved to their target values """
    def __init__(self, cue):
        super(CueRunning, self).__init__(cue.cue_number, cue.fade_time)
        for channel in cue.channels:
            self.channels.append(ChannelTarget(channel.channel_number, channel.channel_value))

    def __repr__(self):
        return_string = ('CueRunning(cue_number=%s, fade_time=%s)'
                         % (repr(self.cue_number), repr(self.fade_time)))

        for channel in self.channels:
            return_string = return_string + '\n\t' + str(channel)

        return return_string

    def step_channels(self):
        """ Trigger step on all channels """
        for channel in self.channels:
            channel.step()

    def remove_static_channels(self):
        """ Remove all channels at their target values """
        new_channels = []
        for channel in self.channels:
            if channel.direction() != STATIC:
                new_channels.append(channel)
        self.channels = new_channels

    def from_json(self, json_string):
        """ Return new CueRunning object from json string """
        loaded_cue = json.loads(json_string)
        cue_copy = Cue(loaded_cue["cue_number"], loaded_cue["fade_time"])
        for channel in loaded_cue["channels"]:
            cue_copy.add_channel(channel["channel_number"], channel["target_value"])
        cue_copy_running = CueRunning(cue_copy)
        return cue_copy_running

    def set_running(self, current_channels):
        """ Set all channels of CueRunning to running """
        for channel in self.channels:
            channel.set_running(current_channels, self.fade_time)


class CueList(object):
    """ CueList holds a list of static cues ready to be handed to CueListRunning """
    def __init__(self, cue_list_number):
        self.cue_list_number = cue_list_number
        self.cues = []

    def __repr__(self):
        return_string = ('CueList(cue_list_number=%s)'
                         % (repr(self.cue_list_number)))

        for cue in self.cues:
            return_string = return_string + ('\n\tCue(cue_number=%s, fade_time=%s)'
                                             % (repr(cue.cue_number), repr(cue.fade_time)))

            for channel in cue.channels:
                return_string = return_string + '\n\t\t' + str(channel)

        return return_string

    def add_cue(self, cue):
        """ Add cue to cue list """
        self.cues.append(cue)

    def remove_cue(self, cue_number):
        """ Remove cue from cue list"""
        new_cues = []
        for cue in self.cues:
            if cue.cue_number != cue_number:
                new_cues.append(cue)
        self.cues = new_cues

    def to_json(self):
        """ Return CueList as a json string """
        return_string = "{\"cue_list_number\": " + str(self.cue_list_number) + ", \"cues\": "
        return_string = return_string + "["
        for cue in self.cues:
            return_string = return_string + cue.to_json()
            return_string = return_string + ","
        return_string = return_string[:-1] + "]}"

        return return_string

    def from_json(self, json_string):
        """ Return new CueList object from json string """
        loaded_cue_list = json.loads(json_string)
        cue_list_copy = CueList(loaded_cue_list["cue_list_number"])
        cue_to_add = Cue(0, 0)
        for cue in loaded_cue_list["cues"]:
            cue_list_copy.add_cue(cue_to_add.from_json(json.dumps(cue)))
        return cue_list_copy


class CueListRunning(CueList):
    """ CueListRunning expands CueList and allows stepping of all cues towards their goal as well as merging their output """
    def __init__(self, cue_list_number):
        super(CueListRunning, self).__init__(cue_list_number)

    def __repr__(self):
        return_string = ('CueListRunning(cue_list_number=%s)'
                         % (repr(self.cue_list_number)))

        for cue in self.cues:
            return_string = return_string + ('\n\tCueRunning(cue_number=%s, fade_time=%s)'
                                             % (repr(cue.cue_number), repr(cue.fade_time)))

            for channel in cue.channels:
                return_string = return_string + '\n\t\t' + str(channel)

        return return_string

    def add_cue(self, cue, current_channels):
        """ Add cue to cue list """
        self.cues.append(CueRunning(copy.deepcopy(cue)))
        self.cues[-1].set_running(current_channels)

    def step_cues(self):
        """ Step all cues in cue list """
        for cue in self.cues:
            cue.step_channels()

    def merge_cue_levels(self, mode):
        """ Merge and return all running cues into one result """
        if len(self.cues) == 1:
            # If we have one running cue, no merge needed, just return this cue channel set
            static_channels = []

            for channel in self.cues[0].channels:
                static_channels.append(Channel(channel.channel_number, channel.channel_value))

            return static_channels

        if len(self.cues) == 0:
            # If we have no running cues, return an empty channel list
            return []

        elif mode == HTP:
            # Merge taking highest value for all channels
            # Get oldest running cue, convert to static values and to use as base
            static_channels = []

            for channel in self.cues[0].channels:
                static_channels.append(Channel(channel.channel_number, channel.channel_value))

            # Itterate over the channels in all other cues
            # if channel doesn't exist, add it, if it does check if new value is higher and if so update it
            for cue in self.cues:
                for channel in cue.channels:
                    found = False
                    for s_channel in static_channels:
                        if s_channel.channel_number == channel.channel_number:
                            if s_channel.channel_value < channel.target_value:
                                s_channel.channel_value = channel.target_value
                            found = True
                    if found is False:
                        static_channels.append(Channel(channel.channel_number, channel.channel_value))

            return static_channels

        elif mode == LTP:
            # Merge taking highest value for all channels
            # Get oldest running cue, convert to static values and to use as base
            static_channels = []

            for channel in self.cues[0].channels:
                static_channels.append(Channel(channel.channel_number, channel.channel_value))

            # Itterate over the channels in all other cues
            # if channel doesn't exist, add it, if it does check if new value is higher and if so update it
            for cue in self.cues:
                for channel in cue.channels:
                    found = False
                    for s_channel in static_channels:
                        if s_channel.channel_number == channel.channel_number:
                            s_channel.channel_value = channel.target_value
                            found = True
                    if found is False:
                        static_channels.append(Channel(channel.channel_number, channel.channel_value))

            return static_channels

    def remove_static_channels(self):
        """ Remove any channels who have reached their target value """
        for cue in self.cues:
            cue.remove_static_channels()

    def remove_empty_cues(self):
        """ Remove any cues who have no target channels left """
        for cue in self.cues:
            if len(cue.channels) == 0:
                self.remove_cue(cue.cue_number)

    def tick_cues(self, merge_type):
        """ Return a merge of all running cues and clean up static and empty objects """
        self.step_cues()
        return_merge = self.merge_cue_levels(merge_type)
        self.remove_static_channels()
        self.remove_empty_cues()
        return return_merge


class Universe(object):
    """ A universe of channels """
    def __init__(self, number_of_channels):
        super(Universe, self).__init__()
        self.channels = []

        for x in range(number_of_channels):
            self.channels.append(Channel(x + 1, 0))

    def __repr__(self):
        return_string = "Universe()"

        for channel in self.channels:
            return_string = return_string + '\n\t' + str(channel)

        return return_string

    def merge_values(self, channel_array):
        """ Take a list of static channels and update out universe where needed """
        for channel in channel_array:
            self.channels[channel.channel_number - 1].channel_value = channel.channel_value
