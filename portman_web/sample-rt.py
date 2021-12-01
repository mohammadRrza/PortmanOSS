# from rtkit.resource import RTResource
# from rtkit.authenticators import BasicAuthenticator, CookieAuthenticator
# from rtkit.errors import RTResourceError
#
# from rtkit import set_logging
# import logging
# set_logging('debug')
# logger = logging.getLogger('rtkit')
#
# resource = RTResource('https://5.202.129.65/rt/REST/1.0/',
#                       'complaint@pishgaman.net', 'pishgaman@12', CookieAuthenticator)
#
# QUEUE_CEM = 19
# QUEUE_COMPLAINTS = 106
#
#
# def subject_ticket():
#     content = {
#     'content': {
#         'Queue': 'rt-noc',
#         'Subject': 'New Ticket -- Test from OSS',
#         'Text': 'My useless\ntext on\nthree lines.',
#         }
#     }
#     try:
#         response = resource.post(path='ticket/new', payload=content,)
#         logger.info(response.parsed)
#         logger.info('=================> %s'%response.parsed[0][0][1].split('/')[1])
#     except RTResourceError as e:
#         logger.error(e.response.status_int)
#         logger.error(e.response.status)
#         logger.error(e.response.parsed)
#
#
# def get_ticket_info(ticket_id):
#     reply_list = []
#     try:
#         response = resource.get(path='ticket/%s/show'%ticket_id)
#         print response.parsed
#         #response = resource.get(path='ticket/%s/history?format=l'%ticket_id)
#         for r in response.parsed:
#             is_reply = False
#             content = ''
#             for t in r:
#                 if t[0] == 'Content':
#                     content = t[1]
#                 elif t[0] == 'Type' and t[1] == 'Correspond':
#                     is_reply = True
#
#
#                 logger.info(t)
#             if is_reply and content:
#                 reply_list.append(content)
#
#     except RTResourceError as e:
#         print e
#         logger.error(e.response.status_int)
#         logger.error(e.response.status)
#         logger.error(e.response.parsed)
#     print reply_list
#
# if __name__=='__main__':
#     print subject_ticket()
# #    print get_ticket_info(11596)
# #    print get_ticket_info(33216)
#
