"""
    test_12_listing_publish

    As a developer working with an Ocean marketplace,
    I need a way to unpublish my asset (i.e. remove relevant listings) from a marketplace

"""

import secrets

from starfish.asset import MemoryAsset


def test_10_asset_upload(surfer_agent, metadata):
    test_data = secrets.token_hex(1024)
    asset = MemoryAsset(metadata=metadata, data=test_data)
    listing = surfer_agent.register_asset(asset)
    assert(listing)
    assert(listing.asset)
    print(listing.listing_id, listing.asset.asset_id)

    assert(not listing.is_published)

    listing.set_published(True)
    assert(listing.is_published)

    assert(surfer_agent.update_listing(listing))

    read_listing = surfer_agent.get_listing(listing.listing_id)
    assert(read_listing)
    assert(read_listing.is_published)
