class ChannelsHandler:
    def add_channel(self, channel_link, frequency):
        """
@parameter {str} channel_link Either a t.me link or @ChannelName
@parameter {float} frequency How often (in hours) do I have to check
    new messages in the channel
@returns {NoneType} None
        """
        pass

    def edit_channel(self, channel_link, new_frequency):
        """
@parameter {str} channel_link Either a t.me link or @ChannelName
@parameter {float} new_frequency How often (in hours) do I have to check
    new messages in the channel
@returns {NoneType} None
        """
        pass

    def del_channel(self, channel_link):
        """
@parameter {str} channel_link Either a t.me link or @ChannelName
@returns {NoneType} None
        """
        pass
