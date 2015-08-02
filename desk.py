import json

DOWN = -1
UP = 1
STATIC = 0
HTP = 0
LTP = 1


class Channel(object):

    def __init__(self, channel_number, channel_value):
        self.channel_number = channel_number
        self.channel_value = channel_value

    def __repr__(self):
        return ('Channel(channel_number=%s, channel_value=%s)'
                % (repr(self.channel_number), repr(self.channel_value)))


class ChannelTarget(Channel):

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

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True)


class Cue(object):

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
            self.channels.append(ChannelTarget(channel_number, target_value))

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
        return_string = "{\"cue_number\": " + str(self.cue_number) + ", \"channels\": "
        return_string = return_string + "["
        for channel in self.channels:
            return_string = return_string + channel.to_json()
            return_string = return_string + ","
        return_string = return_string[:-1] + "], \"fade_time\": " + str(self.fade_time) + "}"

        return return_string

    def from_json(self, json_string):
        loaded_cue = json.loads(json_string)
        cue_copy = Cue(loaded_cue["cue_number"], loaded_cue["fade_time"])
        for channel in loaded_cue["channels"]:
            cue_copy.add_channel(channel["channel_number"], channel["target_value"])
        return cue_copy


class CueRunning(Cue):

    def __init__(self, cue):
        super(CueRunning, self).__init__(cue.cue_number, cue.fade_time)
        self.channels = cue.channels

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
        loaded_cue = json.loads(json_string)
        cue_copy = Cue(loaded_cue["cue_number"], loaded_cue["fade_time"])
        for channel in loaded_cue["channels"]:
            cue_copy.add_channel(channel["channel_number"], channel["target_value"])
        cue_copy_running = CueRunning(cue_copy)
        return cue_copy_running


class CueList(object):

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
        return_string = "{\"cue_list_number\": " + str(self.cue_list_number) + ", \"cues\": "
        return_string = return_string + "["
        for cue in self.cues:
            return_string = return_string + cue.to_json()
            return_string = return_string + ","
        return_string = return_string[:-1] + "]}"

        return return_string

    def from_json(self, json_string):
        loaded_cue_list = json.loads(json_string)
        cue_list_copy = CueList(loaded_cue_list["cue_list_number"])
        cue_to_add = Cue(0, 0)
        for cue in loaded_cue_list["cues"]:
            cue_list_copy.add_cue(cue_to_add.from_json(json.dumps(cue)))
        return cue_list_copy


class CueListRunning(CueList):

    def __init__(self, cue_list):
        super(CueListRunning, self).__init__(cue_list.cue_list_number)
        self.cues = []
        test_cue = CueRunning(Cue(0, 0))
        for cue in cue_list.cues:
            self.cues.append(test_cue.from_json(cue.to_json()))

    def __repr__(self):
        return_string = ('CueListRunning(cue_list_number=%s)'
                         % (repr(self.cue_list_number)))

        for cue in self.cues:
            return_string = return_string + ('\n\tCueRunning(cue_number=%s, fade_time=%s)'
                                             % (repr(cue.cue_number), repr(cue.fade_time)))

            for channel in cue.channels:
                return_string = return_string + '\n\t\t' + str(channel)

        return return_string

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

    def remove_static_channels(self):
        for cue in self.cues:
            cue.remove_static_channels()

    def remove_empty_cues(self):
        for cue in self.cues:
            if len(cue.channels) == 0:
                self.remove_cue(cue.cue_number)
