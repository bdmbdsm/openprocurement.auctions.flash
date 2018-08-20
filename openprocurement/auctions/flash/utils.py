# -*- coding: utf-8 -*-
from openprocurement.api.constants import TZ
from logging import getLogger
from pkg_resources import get_distribution
from openprocurement.api.utils import (
    context_unpack,
    get_now
)
from openprocurement.auctions.core.utils import (
    check_complaint_status,
    remove_draft_bids,
    check_bids
)
PKG = get_distribution(__package__)
LOGGER = getLogger(PKG.project_name)


def check_status_flash(request):
    auction = request.validated['auction']
    now = get_now()
    for complaint in auction.complaints:
        check_complaint_status(request, complaint, now)
    for award in auction.awards:
        for complaint in award.complaints:
            check_complaint_status(request, complaint, now)
    if (
        auction.status == 'active.enquiries'
        and not auction.tenderPeriod.startDate
        and auction.enquiryPeriod.endDate.astimezone(TZ)
        <= now
    ):
        LOGGER.info(
            'Switched auction %s to %s', auction.id, 'active.tendering', extra=context_unpack(
                request, {
                    'MESSAGE_ID': 'switched_auction_active.tendering'}))
        auction.status = 'active.tendering'
        return
    elif (
        auction.status == 'active.enquiries'
        and auction.tenderPeriod.startDate
        and auction.tenderPeriod.startDate.astimezone(TZ)
        <= now
    ):
        LOGGER.info(
            'Switched auction %s to %s', auction.id, 'active.tendering', extra=context_unpack(
                request, {
                    'MESSAGE_ID': 'switched_auction_active.tendering'}))
        auction.status = 'active.tendering'
        return
    elif not auction.lots and auction.status == 'active.tendering' and auction.tenderPeriod.endDate <= now:
        LOGGER.info('Switched auction %s to %s',
                    auction['id'],
                    'active.auction',
                    extra=context_unpack(request,
                                         {'MESSAGE_ID': 'switched_auction_active.auction'}))
        auction.status = 'active.auction'
        remove_draft_bids(request)
        check_bids(request)
        if auction.numberOfBids < 2 and auction.auctionPeriod:
            auction.auctionPeriod.startDate = None
        return
    elif auction.lots and auction.status == 'active.tendering' and auction.tenderPeriod.endDate <= now:
        LOGGER.info('Switched auction %s to %s',
                    auction['id'],
                    'active.auction',
                    extra=context_unpack(request,
                                         {'MESSAGE_ID': 'switched_auction_active.auction'}))
        auction.status = 'active.auction'
        remove_draft_bids(request)
        check_bids(request)
        _ = [setattr(i.auctionPeriod, 'startDate', None)  # noqa: F841
             for i in auction.lots if i.numberOfBids < 2 and i.auctionPeriod]
        return
    elif not auction.lots and auction.status == 'active.awarded':
        standStillEnds = [
            a.complaintPeriod.endDate.astimezone(TZ)
            for a in auction.awards
            if a.complaintPeriod.endDate
        ]
        if not standStillEnds:
            return
        standStillEnd = max(standStillEnds)
        if standStillEnd <= now:
            check_auction_status(request)
    elif auction.lots and auction.status in ['active.qualification', 'active.awarded']:
        if any([i['status'] in auction.block_complaint_status and i.relatedLot is None for i in auction.complaints]):
            return
        for lot in auction.lots:
            if lot['status'] != 'active':
                continue
            lot_awards = [i for i in auction.awards if i.lotID == lot.id]
            standStillEnds = [
                a.complaintPeriod.endDate.astimezone(TZ)
                for a in lot_awards
                if a.complaintPeriod.endDate
            ]
            if not standStillEnds:
                continue
            standStillEnd = max(standStillEnds)
            if standStillEnd <= now:
                check_auction_status(request)
                return


def check_auction_status(request):
    auction = request.validated['auction']
    now = get_now()
    if auction.lots:
        if any([i.status in auction.block_complaint_status and i.relatedLot is None for i in auction.complaints]):
            return
        for lot in auction.lots:
            if lot.status != 'active':
                continue
            lot_awards = [i for i in auction.awards if i.lotID == lot.id]
            if not lot_awards:
                continue
            last_award = lot_awards[-1]
            pending_complaints = any([
                i['status'] in auction.block_complaint_status and i.relatedLot == lot.id
                for i in auction.complaints
            ])
            pending_awards_complaints = any([
                i.status in auction.block_complaint_status
                for a in lot_awards
                for i in a.complaints
            ])
            stand_still_end = max([
                a.complaintPeriod.endDate or now
                for a in lot_awards
            ])
            if pending_complaints or pending_awards_complaints or not stand_still_end <= now:
                continue
            elif last_award.status == 'unsuccessful':
                LOGGER.info('Switched lot %s of auction %s to %s',
                            lot.id,
                            auction.id,
                            'unsuccessful',
                            extra=context_unpack(request,
                                                 {'MESSAGE_ID': 'switched_lot_unsuccessful'},
                                                 {'LOT_ID': lot.id}))
                lot.status = 'unsuccessful'
                continue
            elif (
                last_award.status == 'active'
                and any([i.status == 'active' and i.awardID == last_award.id for i in auction.contracts])
            ):
                LOGGER.info('Switched lot %s of auction %s to %s',
                            lot.id,
                            auction.id,
                            'complete',
                            extra=context_unpack(request,
                                                 {'MESSAGE_ID': 'switched_lot_complete'},
                                                 {'LOT_ID': lot.id}))
                lot.status = 'complete'
        statuses = set([lot.status for lot in auction.lots])
        if statuses == set(['cancelled']):
            LOGGER.info('Switched lot %s of auction %s to %s',
                        lot.id,
                        auction.id,
                        'cancelled',
                        extra=context_unpack(request,
                                             {'MESSAGE_ID': 'switched_lot_cancelled'},
                                             {'LOT_ID': lot.id}))
            auction.status = 'cancelled'
        elif not statuses.difference(set(['unsuccessful', 'cancelled'])):
            LOGGER.info('Switched lot %s of auction %s to %s',
                        lot.id,
                        auction.id,
                        'unsuccessful',
                        extra=context_unpack(request,
                                             {'MESSAGE_ID': 'switched_lot_unsuccessful'},
                                             {'LOT_ID': lot.id}))
            auction.status = 'unsuccessful'
        elif not statuses.difference(set(['complete', 'unsuccessful', 'cancelled'])):
            LOGGER.info('Switched lot %s of auction %s to %s',
                        lot.id,
                        auction.id,
                        'complete',
                        extra=context_unpack(request,
                                             {'MESSAGE_ID': 'switched_lot_complete'},
                                             {'LOT_ID': lot.id}))
            auction.status = 'complete'
    else:
        pending_complaints = any([
            i.status in auction.block_complaint_status
            for i in auction.complaints
        ])
        pending_awards_complaints = any([
            i.status in auction.block_complaint_status
            for a in auction.awards
            for i in a.complaints
        ])
        stand_still_ends = [
            a.complaintPeriod.endDate
            for a in auction.awards
            if a.complaintPeriod.endDate
        ]
        stand_still_end = max(stand_still_ends) if stand_still_ends else now
        stand_still_time_expired = stand_still_end < now
        last_award_status = auction.awards[-1].status if auction.awards else ''
        if not pending_complaints and not pending_awards_complaints and stand_still_time_expired \
                and last_award_status == 'unsuccessful':
            LOGGER.info(
                'Switched auction %s to %s', auction.id, 'unsuccessful', extra=context_unpack(
                    request, {
                        'MESSAGE_ID': 'switched_auction_unsuccessful'}))
            auction.status = 'unsuccessful'
        if not pending_complaints and not pending_awards_complaints and stand_still_time_expired \
                and last_award_status == 'unsuccessful':
            LOGGER.info(
                'Switched auction %s to %s', auction.id, 'unsuccessful', extra=context_unpack(
                    request, {
                        'MESSAGE_ID': 'switched_auction_unsuccessful'}))
            auction.status = 'unsuccessful'
        if auction.contracts and auction.contracts[-1].status == 'active':
            LOGGER.info(
                'Switched auction %s to %s', auction.id, 'unsuccessful', extra=context_unpack(
                    request, {
                        'MESSAGE_ID': 'switched_auction_complete'}))
            auction.status = 'complete'