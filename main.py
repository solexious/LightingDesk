DOWN = -1
UP = 1
STATIC = 0
HTP = 0
LTP = 1


class Channel(object):
    channel_number = 0
    channel_value = 0

    def __init__(self, channel_number, channel_value):
        self.channel_number = channel_number
        self.channel_value = channel_value

    def __repr__(self):
        return ('Channel(channel_number=%s, channel_value=%s)'
                % (repr(self.channel_number), repr(self.channel_value)))


class ChannelTarget(Channel):
    target_value = 0
    step_amount = 1

    def __init__(self, channel_number, target_value):
        super(ChannelTarget, self).__init__(channel_number, 0)
        self.target_value = target_value

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


class Cue(object):
    cue_number = 0
    channels = []
    fade_time = 0

    def __init__(self, cue_number, fade_time):
        self.cue_number = cue_number
        self.fade_time = fade_time

    def __repr__(self):
        return_string = ('Cue(cue_number=%s, fade_time=%s)'
                         % (repr(self.cue_number), repr(self.fade_time)))

        for channel in self.channels:
            return_string = return_string + '\n' + str(channel)

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


class CueRunning(Cue):

    def __init__(self, cue):
        super(CueRunning, self).__init__(cue.cue_number, cue.fade_time)
        self.channels = cue.channels

    def step_channels(self):
        """ Trigger step on all channels """
        for channel in self.channels:
            channel.step()

    def remove_static_channels(self):
        """ Remove all channels at their target values """
        self.channels = [x for x in self.channels if self.channels[x].direction() != STATIC]


class CueList(object):
    cue_list = []

    def add_cue(self, cue):
        """ Add cue to cue list """
        self.cue_list.append(cue)

    def remove_cue(self, cue_number):
        """ Remove cue from cue list"""
        self.cue_list = [x for x in self.cue_list if self.cue_list[x].cue_number != cue_number]

    def step_cues(self):
        """ Step all cues in cue list """
        for cue in self.cue_list:
            cue.step_channels()

    def merge_cue_levels(self, mode):
        """ Merge and return all running cues into one result """
        if len(self.cue_list) == 1:
            # If we have one running cue, no merge needed, just return this cue channel set
            static_channels = []

            for channel in self.cue_list[0].channels:
                static_channels.append(Channel(channel.channel_number, channel.channel_value))

            return static_channels

        if len(self.cue_list) == 0:
            # If we have no running cues, return an empty channel list
            return []

        elif mode == HTP:
            # Merge taking highest value for all channels
            # Get oldest running cue, convert to static values and to use as base
            static_channels = []

            for channel in self.cue_list[0].channels:
                static_channels.append(Channel(channel.channel_number, channel.channel_value))

            # Itterate over the channels in all other cues
            # if channel doesn't exist, add it, if it does check if new value is higher and if so update it
            for cue in self.cue_list:
                for channel in cue.channels:
                    found = False
                    for s_channel in static_channels:
                        if s_channel.channel_number == channel.channel_number:
                            s_channel.target_value = channel.target_value
                            found = True
                    if found is False:
                        static_channels.append(Channel(channel.channel_number, channel.channel_value))

            return static_channels

# channel1 = ChannelTarget(1,0)
# print channel1

cue1 = Cue(1, 5)
cue1.add_channel(1, 0)
cue1.add_channel(2, 1)
cue1.remove_channel(1)
cue1running = CueRunning(cue1)
print cue1
print cue1running

# cue1.add_channel(3, 5)
# print cue1
# print cue1running

# cue1running.step_channels()
# print cue1

# cue1running.step_channels()
# print cue1
