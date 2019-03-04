from ixmp.reporting import Reporter as IXMPReporter


class Reporter(IXMPReporter):
    """MESSAGEix Reporter.

    """
    def __init__(self):
        # TODO add MESSAGE_ix specific nodes from a file
        super(Reporter, self).__init__(self)
