from odoo import models, fields, api, exceptions, _ 
from datetime import date, datetime
from odoo.exceptions import ValidationError


class AccountCheque(models.Model):
	_inherit = "account.cheque"

	batch_account_cheque_id  =  fields.Many2one('account.cheque.batch', 'Batch Account Cheque')

	@api.multi
	def _active_journal_items(self):
		list_of_move_line = []
		for journal_items in self:
			journal_item_ids = self.env['account.move'].search([('account_cheque_id','=',journal_items.id)])
		for move in journal_item_ids:
			for line in move.line_ids:
				list_of_move_line.append(line.id)

		journal_item_ids = False
		for journal_items in self:
			if journal_items.batch_account_cheque_id:
				journal_item_ids = self.env['account.move'].search([('batch_account_cheque_id','=',journal_items.batch_account_cheque_id.id)])

		if journal_item_ids:
			for move in journal_item_ids:
				for line in move.line_ids:
					list_of_move_line.append(line.id)

		item_count = len(list_of_move_line)
		journal_items.journal_items_count = item_count
		return

	@api.multi
	def action_view_jornal_items(self):
		list_of_move_line = []
		for journal_items in self:
			journal_item_ids = self.env['account.move'].search([('account_cheque_id','=',journal_items.id)])
		for move in journal_item_ids:
			for line in move.line_ids:
				list_of_move_line.append(line.id)

		for journal_items in self:
			if journal_items.batch_account_cheque_id:
				journal_item_ids = self.env['account.move'].search([('batch_account_cheque_id','=',journal_items.batch_account_cheque_id.id)])

		if journal_item_ids:
			for move in journal_item_ids:
				for line in move.line_ids:
					list_of_move_line.append(line.id)

		item_count = len(list_of_move_line)
		journal_items.journal_items_count = item_count
		return {
            'name': 'Journal Items',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': 'account.move.line',
            'domain': [('id', '=', list_of_move_line)],
        }


class AccountMove(models.Model):
	_inherit='account.move'

	batch_account_cheque_id  =  fields.Many2one('account.cheque.batch', 'Batch Account Cheque')


class BatchAccountCheque(models.Model):
	_name = "account.cheque.batch"
	_rec_name = 'reference'

	def _default_selected_acc_cheque(self):
		items = []
		for cheque in  self.env['account.cheque'].browse(self._context.get('active_ids')):
			#if cheque.status1 in ['draft', 'registered'] and cheque.account_cheque_type == 'incoming':
			if cheque.status1 in ['registered'] and cheque.account_cheque_type == 'incoming':
				items.append(cheque.id)
		return items

	@api.depends('account_cheque_ids.amount')
	def _amount_all(self):
		for batch_cheque in self:
			amount = 0.0
			for cheque in batch_cheque.account_cheque_ids:
				amount += cheque.amount
			batch_cheque.update({
				'amount_total': amount
				})

	reference = fields.Char(string='Reference Number')
	date = fields.Date(default=fields.Datetime.now())

	account_cheque_ids = fields.Many2many('account.cheque', default=_default_selected_acc_cheque)

	credit_account_id = fields.Many2one('account.account',string="Credit Account")
	debit_account_id = fields.Many2one('account.account',sring="Debit Account")
	journal_id = fields.Many2one('account.journal',string="Journal",required=True)
	company_id = fields.Many2one('res.company',string="Company",required=True)

	status = fields.Selection([('draft','Draft'),('registered','Registered'),('deposited','Deposited')],string="Status",default="draft",copy=False, index=True, track_visibility='onchange')


	amount_total = fields.Monetary(string='Total', store=True, readonly=True, compute='_amount_all', track_visibility='always')
	currency_id = fields.Many2one("res.currency", string="Currency", readonly=True, required=True)



	@api.multi
	def getPages(self):
		self.ensure_one()
		PAGE_STRONG = "_PAGE"
		int_page = 1
		TOTAL_CHAR_PER_PAGE = 333
		current_total_char_per_page = 0
		data_list = {}
		#raise Warning(self.account_cheque_ids)

		for account_cheque_id in self.account_cheque_ids:
			total_bank_name = len(account_cheque_id and account_cheque_id.bank_id and account_cheque_id.bank_id.name or '')
			total_cheque_number = len(account_cheque_id and account_cheque_id.cheque_number or '')
			total_cheque_amount = len(str(account_cheque_id.amount))
			total_length = total_bank_name + total_cheque_number + total_cheque_amount

			if current_total_char_per_page + total_length < TOTAL_CHAR_PER_PAGE:
				str_page = str(int_page).zfill(4) + PAGE_STRONG
				if not str_page in data_list:
					data_list[str_page] = [self,[]]
				data_list[str_page][1].append(account_cheque_id)
				current_total_char_per_page += total_length
			else:
				int_page += 1
				str_page = str(int_page).zfill(4) + PAGE_STRONG
				if not str_page in data_list:
					data_list[str_page] = [self,[]]
				data_list[str_page][1].append(account_cheque_id)
				current_total_char_per_page = total_length

		if len(data_list) > 0:
			#raise Warning(data_list)
			return data_list

		return False



	@api.model
	def default_get(self, flds):
		result = super(BatchAccountCheque, self).default_get(flds)
		user_company_id = self.env.user.company_id
		result['credit_account_id'] = user_company_id.in_credit_account_id.id
		result['debit_account_id'] = user_company_id.in_debit_account_id.id
		result['journal_id'] = user_company_id.specific_journal_id.id
		result['company_id'] = user_company_id.id
		result['currency_id'] = user_company_id.currency_id.id
		return result

	def unlink(self):
		stat = {'registered': 'Registered','deposited': 'Deposited'}
		#if 'deposited' in self.mapped('status') or 'registered' in self.mapped('status'):
		if 'deposited' in self.mapped('status'):
			raise ValidationError(_('Batch Incoming Cheque/s cannot be delete. Status is already %s.' % (stat[self.mapped('status')[0]] )))
		return super(BatchAccountCheque, self).unlink()

	@api.one
	def set_batch_submit_deposit(self):

		for account_cheque_id in self.account_cheque_ids:
			if account_cheque_id.status1 in ['deposited']:
				stat = {'registered': 'Registered','deposited': 'Deposited'}
				raise ValidationError(_('Batch Incoming Cheque cannot be process.\n\n Cheque %s is already %s. \n\n Please Remove the Cheque.' % (account_cheque_id.sequence ,stat[account_cheque_id.status1] )))

		if not self.account_cheque_ids:
			raise ValidationError(_('Please add an Incoming Cheque/s.'))

		account_move_obj = self.env['account.move']
		move_lines = []		

		#Override All the Selected Cheque Data Before Creating a Journal
		#for account_cheque_id in self.account_cheque_ids:
			#if account_cheque_id.status1 == 'draft':
		#	account_cheque_id.write({
					#'credit_account_id': self.credit_account_id.id,
					#'debit_account_id': self.debit_account_id.id,
					#'journal_id': self.journal_id.id,
					#'company_id': self.company_id.id,
		#			'batch_account_cheque_id': self.id,})

		total_check_amt = 0.00
		str_ref = ""
		str_ref_dep = ""

		#for account_cheque_id in self.account_cheque_ids:
			#if account_cheque_id.status1 == 'draft':
		#	str_ref += account_cheque_id.sequence + ' - ' + account_cheque_id.cheque_number + ', '
		#	total_check_amt += account_cheque_id.amount

		#str_ref_dep = str_ref

		#str_ref += " Registered"
		#str_ref_dep +=" Deposited"

		# Submit First
		#Account Move
		#vals = {
		#		'name' : self.reference,
		#		'date' : self.date,
		#		'journal_id' : self.journal_id.id,
		#		'company_id' : self.company_id.id,
		#		'state' : 'draft',
		#		'ref' : str_ref,
		#		'batch_account_cheque_id' : self.id}
		#account_move = account_move_obj.create(vals)

		#debit_vals = {
		#		#'partner_id' : self.payee_user_id.id,
		#		'account_id' : self.debit_account_id.id, 
		#		'debit' : total_check_amt,
		#		'date_maturity' : datetime.now(),
		#		'move_id' : account_move.id,
		#		'company_id' : self.company_id.id,}

		#move_lines.append((0, 0, debit_vals))		

		#credit_vals = {
		#		#'partner_id' : self.payee_user_id.id,
		#		'account_id' : self.credit_account_id.id, 
		#		'credit' : total_check_amt,
		#		'date_maturity' : datetime.now(),
		#		'move_id' : account_move.id,
		#		'company_id' : self.company_id.id,}

		#move_lines.append((0, 0, credit_vals))
		#account_move.write({'line_ids' : move_lines})
		

		#for account_cheque_id in self.account_cheque_ids:
		#	account_cheque_id.write({
		#			'status1': 'registered'})
		#self.write({'status':'registered'})

		#Then Deposit
		#Account Move
		move_lines = []
		account_move = False
		total_check_amt = 0.00

		for account_cheque_id in self.account_cheque_ids:
			str_ref_dep += account_cheque_id.sequence + ' - ' + account_cheque_id.cheque_number + ', '
			total_check_amt += account_cheque_id.amount
			account_cheque_id.write({'batch_account_cheque_id': self.id,})

		str_ref_dep +=" Deposited"


		vals = {
			'name' : self.reference,
			'date' : self.date,
			'journal_id' : self.journal_id.id,
			'company_id' : self.company_id.id,
			'state' : 'draft',
			'ref' : str_ref_dep,
			'batch_account_cheque_id' : self.id}
		account_move = account_move_obj.create(vals)

		debit_vals = {
			#'partner_id' : self.payee_user_id.id,
			'account_id' : self.env.user.company_id.deposite_account_id.id, 
			'debit' : total_check_amt,
			'date_maturity' : datetime.now(),
			'move_id' : account_move.id,
			'company_id' : self.company_id.id,}
		move_lines.append((0, 0, debit_vals))

		credit_vals = {
			#'partner_id' : self.payee_user_id.id,
			'account_id' : self.debit_account_id.id, 
			'credit' : total_check_amt,
			'date_maturity' : datetime.now(),
			'move_id' : account_move.id,
			'company_id' : self.company_id.id,}
		move_lines.append((0, 0, credit_vals))
		account_move.write({'line_ids' : move_lines})		
		account_move.post()

		for account_cheque_id in self.account_cheque_ids:
			account_cheque_id.write({
					'status1': 'deposited'})
		self.write({'status':'deposited'})

		return True