import numpy as np

from broker.utils.Quota import Quota


class JobQuota(Quota):
    """
    Job quota for a specific client

    @author: Dennis Zyska
    """

    def __call__(self, append=None):
        """
        Check if the quota is exceeded for a specific sid

        :param append: set job key to queue if quota is not exceeded
        :return:
        """
        if self.exceed():
            return True
        else:
            if append:
                pos = (self.queue != 0).argmax(axis=0)
                self.queue[pos] = True
            return False

    def exceed(self):
        """
        Check if the quota is exceeded for a specific sid

        :return: True if quota is exceeded
        """
        if (self.queue == 0).any():
            return False
        else:
            return True

    def reset(self):
        """
        Reset the quota
        """
        self.queue = np.zeros(self.max_len, dtype=np.bool)
