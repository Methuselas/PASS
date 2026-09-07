struct CompanyA {};
struct CompanyZ {};

template <typename Company>
struct MsgSender {
    int sendClear() { return 7; }
};

template <>
struct MsgSender<CompanyZ> {};

template <typename Company>
struct LoggingMsgSender : MsgSender<Company> {
    int send() { return this->sendClear(); }
};

int main() {
    LoggingMsgSender<CompanyZ> sender;
    return sender.send();
}
