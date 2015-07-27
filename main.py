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
    step_amount = 0

    def __init__(self, channel_number, target_value):
        super(ChannelTarget, self).__init__(channel_number, 0)
        self.target_value = target_value

    def __repr__(self):
        return ('ChannelTarget(channel_number=%s, channel_value=%s, target_value=%s, step_amount=%s)' 
            % (repr(self.channel_number), repr(self.channel_value), repr(self.target_value), repr(self.step_amount)))

    def direction(self):
        """ Return channel direction to target value """
        if self.channel_value - self.target_value < 0:
            return UP;
        elif self.channel_value - self.target_value > 0:
            return DOWN;
        else:
            return STATIC;

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

    def addChannel(self, channel_number, target_value):
        """ Add channel to cue unless exists, then update """
        found = False
        for x in self.channels:
            if self.channels[x].channel_number == channel_number:
                found = True
        if found == True:
            self.modifyChannel(channel_number, target_value)
        else:
            self.channels.append(ChannelTarget(channel_number, target_value))

    def removeChannel(self, channel_number):
        """ Remove channel from cue """
        self.channels = [x for x in self.channels if self.channels[x].channel_number != channel_number]

    def modifyChannel(self, channel_number, target_value):
        """ Modify channel if exists """
        for x in self.channels:
            if self.channels[x].channel_number == channel_number:
                self.channels[x].target_value = target_value


class CueRunning(Cue):

    def stepChannels(self):
        """ Trigger step on all channels """
        for x in self.channels:
            self.channels[x].step()

    def removeStaticChannels(self):
        """ Remove all channels at their target values """
        self.channels = [x for x in self.channels if self.channels[x].direction() != STATIC]

class CueList(object):
    cue_list = []

    def addCue(self, cue):
        """ Add cue to cue list """
        self.cue_list.append(cue)

    def removeCue(self, cue_number):
        """ Remove cue from cue list"""
        self.cue_list = [x for x in self.cue_list if self.cue_list[x].cue_number != cue_number]

    def stepCues(self):
        """ Step all cues in cue list """
        for cue in cue_list:
            cue.stepChannels()

    def mergeCueLevels(self, mode):
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
            # Get oldest running cue, convert to static vlaues and to use as base
            static_channels = []

            for channel in self.cue_list[0].channels:
                static_channels.append(Channel(channel.channel_number, channel.channel_value))

            # Itterate over the channels in all other cues, if channel doesn't exist, add it, if it does check if new value is higher and if so update it
            for cue in self.cue_list:
                for channel in cue.channels:
                    found = False
                    for x in static_channels:
                        if static_channels[x].channel_number == channel_number:
                            found = True
                    if found == True:
                        for x in static_channels:
                            if static_channels[x].channel_number == channel_number:
                                static_channels[x].target_value = target_value
                    else:
                        static_channels.append(Channel(channel.channel_number, channel.channel_value))

            return static_channels

channel1 = ChannelTarget(1,0)
print channel1















