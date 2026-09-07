struct CompanyA {};

template <typename Company>
struct MsgSender {
    virtual ~MsgSender() = default;
    virtual int sendClear() { return 7; }
};

template <typename Company>
struct LoggingMsgSender : MsgSender<Company> {
    int send() { return sendClear(); }
};

int main() {
    LoggingMsgSender<CompanyA> sender;
    return sender.send() == 7 ? 0 : 1;
}
