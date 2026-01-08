FelicaError felica_poller_read_blocks(
    FelicaPoller* instance,
    uint8_t block_count,
    const uint8_t* block_list,
    FelicaPollerReadCommandResponse** response) {
    UNUSED(instance);
    UNUSED(block_count);
    UNUSED(block_list);
    UNUSED(response);
    return FelicaErrorProtocol;
}